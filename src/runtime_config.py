# runtime_config.py
# -*- coding: utf-8 -*-
# Central runtime settings, feature toggles, and capability probes

from __future__ import annotations

import os
import platform
import subprocess
from typing import Optional, Dict, Tuple


TRUTHY = {"1", "true", "yes", "on"}
FALSY = {"0", "false", "no", "off"}


class RuntimeConfig:
    """Central runtime configuration and capability probes."""

    DEFAULT_DRY_RUN = True
    _capabilities_cache: Optional[Dict[str, bool]] = None
    _test_allow_real_uploads: bool = False

    # ------------------------------------------------------------------
    # Upload mode helpers
    # ------------------------------------------------------------------
    @classmethod
    def _env_flag(cls, name: str, default: bool = False) -> bool:
        value = os.getenv(name)
        if value is None:
            return default
        lowered = value.strip().lower()
        if lowered in TRUTHY:
            return True
        if lowered in FALSY:
            return False
        return default

    @classmethod
    def allow_real_uploads_for_tests(cls):
        """Allow real uploads (intended for automated tests)."""
        cls._test_allow_real_uploads = True

    @classmethod
    def disable_real_uploads_for_tests(cls):
        """Disable real uploads (restore default dry-run behaviour)."""
        cls._test_allow_real_uploads = False

    @classmethod
    def resolve_upload_mode(cls, requested: Optional[bool]) -> bool:
        """Resolve whether uploads should run in dry-run mode."""
        allow_real = cls._env_flag("DY_ALLOW_REAL_UPLOADS", False) or cls._test_allow_real_uploads
        if not allow_real:
            if requested is False:
                raise PermissionError(cls.get_real_upload_block_message())
            return True
        if requested is None:
            return cls.DEFAULT_DRY_RUN
        return requested

    @classmethod
    def get_real_upload_block_message(cls) -> str:
        return (
            "当前环境禁止真实上传。\n"
            "请使用 --dry-run 或 GUI 中的“模拟上传”选项继续。\n"
            "如果你正在运行测试并确实需要执行真实上传，请设置环境变量 "
            "'DY_ALLOW_REAL_UPLOADS=1' 或在测试代码中调用 "
            "runtime_config.RuntimeConfig.allow_real_uploads_for_tests()。"
        )

    # ------------------------------------------------------------------
    # Capability probes
    # ------------------------------------------------------------------
    @classmethod
    def reset_capabilities_cache(cls):
        cls._capabilities_cache = None

    @classmethod
    def get_capabilities(cls) -> Dict[str, bool]:
        if cls._capabilities_cache is None:
            cls._capabilities_cache = {
                "browser_cookie3": cls.check_browser_cookie3(),
                "playwright": cls.check_playwright(),
                "ffmpeg": cls.check_ffmpeg(),
            }
        return cls._capabilities_cache

    @classmethod
    def check_browser_cookie3(cls) -> bool:
        try:
            import browser_cookie3  # noqa: F401
            return True
        except ImportError:
            return False
        except Exception:
            return False

    @classmethod
    def check_playwright(cls) -> bool:
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as playwright:
                try:
                    browser_path = playwright.chromium.executable_path
                    if browser_path and os.path.exists(browser_path):
                        return True
                except Exception:
                    pass
            return cls._has_system_chrome()
        except ImportError:
            return False
        except Exception:
            return False

    @classmethod
    def check_ffmpeg(cls) -> bool:
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            return False

    @classmethod
    def _has_system_chrome(cls) -> bool:
        system_chrome_paths = []
        if platform.system() == "Darwin":
            system_chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            ]
        elif platform.system() == "Windows":
            system_chrome_paths = [
                os.path.expandvars("%PROGRAMFILES%\\Google\\Chrome\\Application\\chrome.exe"),
                os.path.expandvars("%PROGRAMFILES(x86)%\\Google\\Chrome\\Application\\chrome.exe"),
                os.path.expandvars("%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe"),
            ]
        else:
            system_chrome_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
                "/snap/bin/chromium",
            ]
        return any(os.path.exists(path) for path in system_chrome_paths)

    @classmethod
    def get_missing_capabilities_message(cls) -> str:
        capabilities = cls.get_capabilities()
        missing = [name for name, available in capabilities.items() if not available]
        if not missing:
            return ""
        messages = []
        if "browser_cookie3" in missing:
            messages.append(
                "• browser-cookie3: 无法从浏览器提取 Cookie\n"
                "  安装: pip install browser-cookie3"
            )
        if "playwright" in missing:
            messages.append(
                "• Playwright: 无法进行交互式登录\n"
                "  安装: pip install playwright && python -m playwright install chromium"
            )
        if "ffmpeg" in missing:
            messages.append(
                "• ffmpeg: 无法处理视频文件\n"
                "  安装: 请从 https://ffmpeg.org/download.html 下载"
            )
        return "\n".join(messages)

    @classmethod
    def get_capability_guidance(cls, capability: str) -> Tuple[bool, str]:
        capabilities = cls.get_capabilities()
        is_available = capabilities.get(capability, False)
        if is_available:
            return True, ""
        guidance = {
            "browser_cookie3": (
                "browser-cookie3 不可用。\n"
                "这意味着无法自动从浏览器提取 Cookie。\n"
                "您可以：\n"
                "1. 安装 browser-cookie3: pip install browser-cookie3\n"
                "2. 使用交互式登录（需要 Playwright）"
            ),
            "playwright": (
                "Playwright 不可用。\n"
                "这意味着无法进行交互式登录或自动上传。\n"
                "您可以：\n"
                "1. 安装 Playwright: pip install playwright\n"
                "2. 安装浏览器: python -m playwright install chromium\n"
                "3. 确保系统已安装 Chrome 浏览器"
            ),
            "ffmpeg": (
                "ffmpeg 不可用。\n"
                "这意味着无法处理视频文件（如删除帧）。\n"
                "您可以：\n"
                "1. 从 https://ffmpeg.org/download.html 下载并安装\n"
                "2. 在上传时禁用视频处理功能"
            ),
        }
        return False, guidance.get(capability, f"未知功能: {capability}")


def get_runtime_config() -> RuntimeConfig:
    return RuntimeConfig
