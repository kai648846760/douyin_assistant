# uploader.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang

import os
import time
import subprocess
import sys
from playwright.sync_api import sync_playwright, Browser, Page, Playwright, TimeoutError as PlaywrightTimeoutError
from rich.console import Console

console = Console()

def ensure_playwright_browsers():
    """确保Playwright浏览器已安装"""
    try:
        # 尝试启动Playwright来检查浏览器是否可用
        with sync_playwright() as p:
            try:
                # 尝试获取浏览器可执行文件路径
                browser_path = p.chromium.executable_path
                if os.path.exists(browser_path):
                    return True
            except Exception:
                pass
        
        # 如果浏览器不可用，尝试安装
        console.print("[yellow]检测到Playwright浏览器未安装，正在自动安装...[/yellow]")
        result = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            console.print("[green]Playwright浏览器安装成功！[/green]")
            return True
        else:
            console.print(f"[red]Playwright浏览器安装失败: {result.stderr}[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]检查或安装Playwright浏览器时出错: {e}[/red]")
        return False

class Uploader:
    """负责通过模拟浏览器操作上传视频到抖音 (已重构为会话模式，支持批量上传)"""

    def __init__(self, user_data_dir: str):
        self.user_data_dir = os.path.abspath(user_data_dir)
        os.makedirs(self.user_data_dir, exist_ok=True)
        self.playwright: Playwright = None
        self.browser: Browser = None
        print(f"上传器初始化完成。")

    def start_session(self) -> Page:
        """启动Playwright，打开浏览器，并处理一次性登录。返回一个可用的页面对象。"""
        # 确保Playwright浏览器已安装
        if not ensure_playwright_browsers():
            raise RuntimeError("无法安装或使用Playwright浏览器")
            
        self.playwright = sync_playwright().start()
        
        print("正在启动浏览器...")
        self.browser = self.playwright.chromium.launch_persistent_context(
            self.user_data_dir, headless=False, args=['--disable-blink-features=AutomationControlled']
        )
        page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
        
        upload_url = "https://creator.douyin.com/creator-micro/content/upload"
        home_url_fragment = "/creator-micro/home"
        
        page.goto(upload_url, wait_until="domcontentloaded", timeout=60000)
        
        print("正在检查登录状态或等待您登录...")
        while True:
            if page.get_by_role('button', name='上传视频').count() > 0:
                print("‘上传视频’按钮已找到，您已登录！")
                break
            if home_url_fragment in page.url:
                print(f"检测到已跳转到创作者主页，登录成功！")
                break
            print("  [-] 未检测到登录成功信号，等待您扫码登录，5秒后重试...")
            time.sleep(5)
        
        return page

    def upload_single_video(self, page: Page, video_path: str, title: str, tags: list = None) -> bool:
        """在一个已登录的页面上，执行单个视频的上传逻辑。"""
        try:
            print(f"\n>>>>> 开始处理: '{os.path.basename(video_path)}' <<<<<")
            upload_url = "https://creator.douyin.com/creator-micro/content/upload"
            if upload_url not in page.url:
                print("当前不在上传页，正在跳转...")
                page.goto(upload_url, wait_until="domcontentloaded")

            upload_button = page.get_by_role('button', name='上传视频')
            upload_button.wait_for(state="visible", timeout=30000)
            
            with page.expect_file_chooser() as fc_info:
                upload_button.click()
            
            file_chooser = fc_info.value
            file_chooser.set_files(video_path)
            print("  [>] 文件已选择，等待跳转...")

            while True:
                try: page.wait_for_url("**/creator-micro/content/publish**", timeout=3000); break
                except PlaywrightTimeoutError:
                    try: page.wait_for_url("**/creator-micro/content/post/video**", timeout=3000); break
                    except PlaywrightTimeoutError: time.sleep(0.5)
            print("  [>] 已进入编辑页面。")

            title_container = page.get_by_text('作品标题').locator("..").locator("xpath=following-sibling::div[1]").locator("input")
            time.sleep(1)
            if title_container.count() > 0: title_container.fill(title[:30])
            else:
                title_container_v2 = page.locator(".notranslate")
                title_container_v2.click(); page.keyboard.press("Control+KeyA"); page.keyboard.press("Delete"); page.keyboard.type(title); page.keyboard.press("Enter")
            
            if tags:
                tag_area = page.locator(".zone-container")
                for tag in tags: tag_area.type("#" + tag); tag_area.press("Space")
            print("  [>] 标题和标签已填写。")

            while True:
                if page.locator('[class^="long-card"] div:has-text("重新上传")').count() > 0: break
                else: time.sleep(2)
            print("  [>] 视频处理完成。")

            page.get_by_role('button', name="发布", exact=True).click()
            page.wait_for_url("**/creator-micro/content/manage**", timeout=120000)
            print("  [✔] 发布成功！")
            return True

        except Exception as e:
            error_msg = f"上传 '{os.path.basename(video_path)}' 时发生错误: {e}"
            print(f"错误: {error_msg}")
            page.screenshot(path=f"error_{os.path.basename(video_path)}.png")
            return False
            
    def upload_video(self, video_path: str, title: str, tags: list = None):
        """兼容旧的单个上传模式，自包含启动和关闭。"""
        try:
            page = self.start_session()
            return self.upload_single_video(page, video_path, title, tags)
        finally:
            self.end_session()

    def end_session(self):
        """关闭浏览器和Playwright会话。"""
        if self.browser: self.browser.close()
        if self.playwright: self.playwright.stop()
        print("浏览器会话已关闭。")