# account_manager.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang

import json
import browser_cookie3
import os
import asyncio
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional
from playwright.async_api import async_playwright
from rich.console import Console

console = Console()

class AccountManager:
    """负责管理和读取 accounts.json 文件中的账号信息"""
    def ensure_playwright_browsers(self, progress_callback=None):
        """确保Playwright浏览器已安装，特别优化了PyInstaller打包环境下的兼容性
        
        参数:
            progress_callback: 进度回调函数，接收(step, total, message)参数
        """
        def update_progress(step, total, message):
            if progress_callback:
                progress_callback(step, total, message)
            console.print(f"[cyan]{message}[/cyan]")
        
        try:
            update_progress(1, 10, "开始检查Playwright浏览器状态...")
            console.print(f"[cyan]当前环境: {'打包环境 (MEIPASS)' if hasattr(sys, '_MEIPASS') else '开发环境'}[/cyan]")
            console.print(f"[cyan]Python解释器: {sys.executable}[/cyan]")
            
            # 确保不会跳过浏览器下载
            os.environ.pop('PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD', None)
            update_progress(2, 10, "配置环境变量...")
            
            # 设置浏览器路径环境变量，如果runtime hook没有设置
            if 'PLAYWRIGHT_BROWSERS_PATH' not in os.environ:
                home_dir = os.path.expanduser("~")
                if platform.system() == 'Windows':
                    default_browser_path = os.path.join(home_dir, ".playwright_browsers")
                else:
                    default_browser_path = os.path.join(home_dir, ".playwright_browsers")
                
                os.makedirs(default_browser_path, exist_ok=True)
                os.environ['PLAYWRIGHT_BROWSERS_PATH'] = default_browser_path
                console.print(f"[cyan]设置PLAYWRIGHT_BROWSERS_PATH: {default_browser_path}[/cyan]")
            else:
                console.print(f"[cyan]已存在的PLAYWRIGHT_BROWSERS_PATH: {os.environ['PLAYWRIGHT_BROWSERS_PATH']}[/cyan]")
            
            # 尝试启动Playwright来检查浏览器是否可用
            update_progress(3, 10, "检查现有浏览器...")
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def check_playwright():
                    async with async_playwright() as p:
                        try:
                            # 尝试获取浏览器可执行文件路径
                            browser_path = p.chromium.executable_path
                            console.print(f"[cyan]检测到Playwright浏览器路径: {browser_path}[/cyan]")
                            if os.path.exists(browser_path):
                                console.print("[green]Playwright浏览器已安装并可用！[/green]")
                                return True
                            else:
                                console.print(f"[yellow]浏览器路径存在但文件不存在: {browser_path}[/yellow]")
                        except Exception as e:
                            console.print(f"[yellow]无法获取默认浏览器路径: {e}[/yellow]")
                    return False
                
                result = loop.run_until_complete(check_playwright())
                if result:
                    update_progress(10, 10, "浏览器检查完成，已可用！")
                    return True
            except Exception as e:
                console.print(f"[yellow]Playwright初始化异常: {e}[/yellow]")
            
            # 如果浏览器不可用，尝试安装
            update_progress(4, 10, "浏览器未安装，开始自动安装...")
            
            # 尝试多种安装方法
            install_methods = [
                {"name": "标准Playwright安装", "method": self._install_playwright_standard, "step": 5},
                {"name": "备用Playwright安装", "method": self._install_playwright_alternative, "step": 6},
                {"name": "系统Python安装", "method": self._install_playwright_system_python, "step": 7}
            ]
            
            for method_info in install_methods:
                try:
                    update_progress(method_info["step"], 10, f"尝试{method_info['name']}...")
                    success = method_info['method'](progress_callback)
                    if success:
                        console.print(f"[green]{method_info['name']}成功！[/green]")
                        # 安装成功后，验证浏览器是否可用
                        update_progress(8, 10, "验证安装结果...")
                        try:
                            import asyncio
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            async def verify_playwright():
                                async with async_playwright() as p:
                                    browser_path = p.chromium.executable_path
                                    return os.path.exists(browser_path)
                            
                            if loop.run_until_complete(verify_playwright()):
                                update_progress(10, 10, "Playwright浏览器安装并验证成功！")
                                return True
                            else:
                                console.print(f"[red]安装成功但浏览器文件不存在[/red]")
                                continue
                        except Exception as e:
                            console.print(f"[red]安装成功但验证失败: {e}[/red]")
                            continue
                except Exception as e:
                    console.print(f"[red]{method_info['name']}失败: {e}[/red]")
                    continue
            
            # 如果所有安装方法都失败
            update_progress(9, 10, "自动安装失败，检查系统浏览器...")
            console.print("[red]所有安装方法都失败了！[/red]")
            
            # 作为最后的备选，直接使用系统Chrome浏览器（如果有）
            if self._has_system_chrome():
                console.print("[green]检测到系统已安装Chrome浏览器，可以直接使用！[/green]")
                update_progress(10, 10, "将使用系统Chrome浏览器")
                return True
            
            update_progress(10, 10, "安装失败，需要手动安装")
            console.print("[yellow]提示: 请尝试手动运行 'python -m playwright install chromium' 命令[/yellow]")
            return False
            
        except Exception as e:
            update_progress(10, 10, f"安装过程出错: {str(e)}")
            console.print(f"[red]检查或安装Playwright浏览器时出错: {e}[/red]")
            # 记录详细错误信息到临时文件以便调试
            try:
                temp_log = os.path.join(os.environ.get('TEMP', os.environ.get('TMPDIR', '/tmp')), 'playwright_install_error.log')
                with open(temp_log, 'a') as f:
                    f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Error: {str(e)}\n")
                    f.write(f"Is MEIPASS: {hasattr(sys, '_MEIPASS')}\n")
                    f.write(f"Python Executable: {sys.executable}\n")
                    f.write(f"Platform: {platform.system()}\n")
                    f.write(f"PLAYWRIGHT_BROWSERS_PATH: {os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '未设置')}\n")
                    f.write("----------------------------------------\n")
            except:
                pass
            return False

    def _install_playwright_standard(self, progress_callback=None):
        """标准的Playwright安装方法
        
        参数:
            progress_callback: 进度回调函数，接收(step, total, message)参数
        """
        def update_progress(message):
            if progress_callback:
                progress_callback(5, 10, message)
            console.print(f"[cyan]{message}[/cyan]")
        
        # 构建安装命令参数
        install_args = ["-m", "playwright", "install", "chromium"]
        use_cmd = False
        
        # 根据不同环境选择Python解释器
        if hasattr(sys, '_MEIPASS'):
            update_progress("在打包环境中，寻找合适的Python解释器...")
            
            # 首先尝试使用系统Python
            if platform.system() == 'Darwin':  # macOS
                python_exe = '/usr/bin/python3'
                # 备用路径
                if not os.path.exists(python_exe):
                    python_exe = '/usr/local/bin/python3'
            elif platform.system() == 'Windows':  # Windows
                python_exe = 'python'
                # 在Windows上使用cmd执行，确保能找到Python
                process = subprocess.Popen(
                    ['cmd.exe', '/c', 'python'] + install_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                use_cmd = True
            else:  # Linux
                python_exe = '/usr/bin/python3'
                use_cmd = False
            
            if platform.system() != 'Windows' or not use_cmd:
                # 检查Python解释器是否存在
                if not os.path.exists(python_exe) and platform.system() == 'Windows':
                    # 在Windows上，如果python命令不可用，尝试使用py命令
                    python_exe = 'py'
                
                process = subprocess.Popen(
                    [python_exe] + install_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
        else:
            # 非打包环境，使用当前Python解释器
            process = subprocess.Popen(
                [sys.executable] + install_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        
        # 实时显示安装进度
        progress_chars = ["|", "/", "-", "\\"]
        progress_index = 0
        
        update_progress("开始下载Playwright浏览器...")
        for line in process.stdout:
            # 检查是否包含进度信息
            if "downloading" in line.lower() or "extracting" in line.lower():
                progress_index = (progress_index + 1) % len(progress_chars)
                update_progress(f"{progress_chars[progress_index]} {line.strip()}")
            else:
                console.print(f"  [gray]{line.strip()}[/gray]")
        
        # 等待进程完成并获取返回码
        process.wait(timeout=300)
        
        return process.returncode == 0

    def _install_playwright_alternative(self, progress_callback=None):
        """备用的Playwright安装方法，使用pip install playwright
        
        参数:
            progress_callback: 进度回调函数，接收(step, total, message)参数
        """
        def update_progress(message):
            if progress_callback:
                progress_callback(6, 10, message)
            console.print(f"[cyan]{message}[/cyan]")
        
        update_progress("尝试备用安装方法...")
        
        # 在Windows上使用cmd执行
        if platform.system() == 'Windows':
            process = subprocess.Popen(
                ['cmd.exe', '/c', 'pip', 'install', 'playwright'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        else:
            # 其他系统直接使用pip
            process = subprocess.Popen(
                ['pip', 'install', 'playwright'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        
        update_progress("安装playwright包...")
        # 显示安装进度
        for line in process.stdout:
            console.print(f"  [gray]{line.strip()}[/gray]")
        
        process.wait(timeout=300)
        
        if process.returncode != 0:
            return False
        
        # 安装完成后，执行playwright install
        if platform.system() == 'Windows':
            process = subprocess.Popen(
                ['cmd.exe', '/c', 'playwright', 'install', 'chromium'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        else:
            process = subprocess.Popen(
                ['playwright', 'install', 'chromium'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        
        update_progress("下载浏览器文件...")
        # 显示安装进度
        for line in process.stdout:
            console.print(f"  [gray]{line.strip()}[/gray]")
        
        process.wait(timeout=300)
        
        return process.returncode == 0

    def _install_playwright_system_python(self, progress_callback=None):
        """使用系统Python安装Playwright
        
        参数:
            progress_callback: 进度回调函数，接收(step, total, message)参数
        """
        def update_progress(message):
            if progress_callback:
                progress_callback(7, 10, message)
            console.print(f"[cyan]{message}[/cyan]")
        
        update_progress("尝试使用系统Python安装...")
        
        # 获取系统Python路径
        system_python_paths = []
        
        if platform.system() == 'Windows':
            system_python_paths = [
                'python',
                'py',
                os.path.expandvars('%LOCALAPPDATA%\\Programs\\Python\\Python39\\python.exe'),
                os.path.expandvars('%LOCALAPPDATA%\\Programs\\Python\\Python310\\python.exe'),
                os.path.expandvars('%LOCALAPPDATA%\\Programs\\Python\\Python311\\python.exe'),
                os.path.expandvars('%LOCALAPPDATA%\\Programs\\Python\\Python312\\python.exe'),
            ]
        elif platform.system() == 'Darwin':
            system_python_paths = [
                '/usr/bin/python3',
                '/usr/local/bin/python3',
                '/opt/homebrew/bin/python3',
            ]
        else:
            system_python_paths = [
                '/usr/bin/python3',
                '/usr/bin/python',
            ]
        
        # 尝试使用每个系统Python路径
        for python_exe in system_python_paths:
            try:
                update_progress(f"尝试使用系统Python: {python_exe}")
                
                if platform.system() == 'Windows':
                    process = subprocess.Popen(
                        ['cmd.exe', '/c', python_exe, '-m', 'playwright', 'install', 'chromium'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1
                    )
                else:
                    process = subprocess.Popen(
                        [python_exe, '-m', 'playwright', 'install', 'chromium'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1
                    )
                
                # 显示安装进度
                for line in process.stdout:
                    console.print(f"  [gray]{line.strip()}[/gray]")
                
                process.wait(timeout=300)
                
                if process.returncode == 0:
                    update_progress(f"系统Python安装成功！使用了 {python_exe}")
                    return True
            except Exception as e:
                console.print(f"[red]使用{python_exe}失败: {e}[/red]")
                continue
        
        console.print("[red]所有系统Python路径都尝试失败[/red]")
        return False

    def _has_system_chrome(self):
        """检查系统是否已安装Chrome浏览器"""
        # 检查系统Chrome路径
        system_chrome_paths = []
        
        if platform.system() == 'Darwin':  # macOS
            system_chrome_paths = [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
            ]
        elif platform.system() == 'Windows':  # Windows
            system_chrome_paths = [
                os.path.expandvars('%PROGRAMFILES%\\Google\\Chrome\\Application\\chrome.exe'),
                os.path.expandvars('%PROGRAMFILES(x86)%\\Google\\Chrome\\Application\\chrome.exe')
            ]
        else:  # Linux
            system_chrome_paths = [
                '/usr/bin/google-chrome',
                '/usr/bin/chromium-browser'
            ]
        
        # 检查是否有Chrome浏览器可用
        for chrome_path in system_chrome_paths:
            if os.path.exists(chrome_path):
                os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'] = chrome_path
                console.print(f"[green]设置系统Chrome浏览器路径: {chrome_path}[/green]")
                return True
        
        return False

    def __init__(self, file_path: str = None):
        if file_path is None:
            # 动态查找accounts.json文件
            self.file_path = self._find_accounts_file()
        else:
            self.file_path = file_path
        self.accounts = self._load_accounts()

    def _find_accounts_file(self) -> str:
        """查找accounts.json文件，支持多个可能的位置"""
        # 优先查找的路径
        possible_paths = [
            'accounts.json',  # 根目录
            'config/accounts.json',  # config目录
            './accounts.json',
            './config/accounts.json'
        ]

        for path in possible_paths:
            if os.path.exists(path):
                # 只在第一次创建时输出，避免重复信息
                if not hasattr(AccountManager, '_config_found'):
                    print(f"找到账号配置文件: {path}")
                    AccountManager._config_found = True
                return path

        # 如果都没有找到，默认在根目录创建
        if not hasattr(AccountManager, '_config_found'):
            print("未找到账号配置文件，将在根目录创建新的accounts.json")
            AccountManager._config_found = True
        return 'accounts.json'

    def _load_accounts(self) -> List[Dict]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"提示：找不到账号文件 '{self.file_path}'，已为您创建一个新的空文件。")
            with open(self.file_path, 'w', encoding='utf-8') as f: json.dump([], f)
            return []
        except json.JSONDecodeError:
            print(f"错误：账号文件 '{self.file_path}' 格式不正确。"); return []

    def reload_accounts(self):
        """【新增】从文件中强制重新加载账号信息，解决数据同步问题"""
        print("正在从文件重载账号列表...")
        self.accounts = self._load_accounts()

    def _save_accounts(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, indent=2, ensure_ascii=False)
        print(f"账号信息已成功保存到 '{self.file_path}'。")

    def get_account(self, username: str) -> Optional[Dict]:
        for acc in self.accounts:
            if acc.get('username') == username: return acc
        return None

    def list_accounts(self):
        if not self.accounts: print("当前没有配置任何账号。"); return
        print("当前已配置的账号列表：")
        for i, acc in enumerate(self.accounts):
            print(f"{i+1}. 用户名: {acc.get('username')}, 备注: {acc.get('remark', '无')}")

    def add_account(self, username: str, remark: str = ""):
        if self.get_account(username): print(f"错误：用户名为 '{username}' 的账号已存在。"); return

        safe_username = username.replace(' ', '_').replace('.', '')
        user_data_dir = f"./browser_data/{safe_username}"

        # 自动创建用户数据目录
        try:
            os.makedirs(user_data_dir, exist_ok=True)
            print(f"已创建用户数据目录: {user_data_dir}")
        except Exception as e:
            print(f"警告：创建用户数据目录失败: {e}")
            # 即使创建目录失败，也继续添加账号

        new_account = {"username": username, "cookie": "", "user_data_dir": user_data_dir, "remark": remark}
        self.accounts.append(new_account)
        self._save_accounts()
        print(f"成功添加新账号 '{username}'，并自动创建了数据目录。")

    def update_cookie_from_browser(self, username: str, browser_name: str) -> bool:
        account = self.get_account(username)
        if not account: 
            print(f"错误：未在 {self.file_path} 中找到用户名为 '{username}' 的账号。")
            return False

        print(f"正在尝试从 '{browser_name}' 浏览器中获取 'douyin.com' 的Cookie...")
        try:
            cj_func = getattr(browser_cookie3, browser_name)
            cj = cj_func(domain_name=".douyin.com")
            cookie_str = "; ".join([f"{cookie.name}={cookie.value}" for cookie in cj])
            
            if "sessionid" not in cookie_str:
                print(f"错误：未能在 '{browser_name}' 中找到 'douyin.com' 的有效登录Cookie。")
                return False

            account['cookie'] = cookie_str
            self._save_accounts()
            print(f"成功为账号 '{username}' 更新Cookie！")
            return True
        except Exception as e:
            print(f"获取Cookie时发生错误: {e}")
            return False

    def update_cookie_with_playwright(self, username: str, progress_callback=None) -> bool:
        """
        使用Playwright登录抖音并更新Cookie
        
        参数:
            username: 账号名称
            progress_callback: 进度回调函数，接收(step, total, message)参数
            
        返回:
            bool: 是否成功更新Cookie
        """
        account = self.get_account(username)
        if not account:
            print(f"错误：账号 '{username}' 不存在！")
            return False
        
        # 确保Playwright浏览器已安装
        if not self.ensure_playwright_browsers(progress_callback):
            print(f"错误：未能确保Playwright浏览器可用，无法为账号 '{username}' 更新Cookie！")
            return False
        
        print(f"正在使用Playwright为账号 '{username}' 登录抖音并更新Cookie...")
        
        # 创建事件循环来执行异步方法
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 执行异步登录方法
            cookie_str = loop.run_until_complete(self._playwright_login(username))
            
            if cookie_str:
                # 放宽Cookie有效性检查，不再只依赖sessionid
                # 检查Cookie是否包含有效的认证信息
                if len(cookie_str) > 10:  # 只要Cookie字符串不为空且有一定长度，就认为有效
                    account['cookie'] = cookie_str
                    self._save_accounts()
                    print(f"成功为账号 '{username}' 更新Cookie！Cookie长度: {len(cookie_str)}")
                    return True
                else:
                    print("错误：未能获取到有效的登录Cookie，Cookie内容过短。")
                    return False
            else:
                print("错误：未能获取到Cookie，登录失败。")
                return False
        except Exception as e:
            print(f"使用Playwright登录时发生错误: {e}")
            return False
        finally:
            loop.close()
    
    async def _playwright_login(self, username: str) -> Optional[str]:
        """
        异步方法：使用Playwright登录抖音并获取Cookie
        
        参数:
            username: 账号名称
            
        返回:
            str: Cookie字符串，如果登录失败则返回None
        """
        try:
            async with async_playwright() as playwright:
                # 使用有头浏览器进行登录
                browser = await playwright.chromium.launch(
                    headless=False,  # 有头模式，允许用户交互
                    args=[
                        "--start-maximized",  # 最大化窗口
                        "--no-sandbox",  # 禁用沙箱（某些环境下需要）
                    ]
                )
                
                print(f"已启动浏览器，请在浏览器中登录抖音账号 '{username}'")
                
                # 创建浏览器上下文
                context = await browser.new_context(
                    viewport=None,  # 使用系统默认视口
                    accept_downloads=True,  # 允许下载
                )
                
                # 创建一个新的页面
                page = await context.new_page()
                
                # 访问抖音创作者中心
                await page.goto("https://creator.douyin.com/")
                
                print("\n========= 登录说明 =========")
                print(f"1. 请在打开的浏览器中完成抖音账号 '{username}' 的登录")
                print("2. 系统会自动检测登录状态，无需手动操作控制台")
                print("3. 登录成功后系统将保存cookie到配置文件")
                print("==========================\n")
                
                # 等待用户登录，定期检查是否已登录成功
                login_check_interval = 5  # 每5秒检查一次
                max_wait_time = 300  # 最多等待5分钟
                elapsed_time = 0
                login_successful = False
                
                while elapsed_time < max_wait_time:
                    # 等待一段时间后再次检查
                    await asyncio.sleep(login_check_interval)
                    
                    try:
                        # 检查是否存在登录按钮，添加try-except处理执行上下文被销毁的情况
                        try:
                            has_phone_login = await page.get_by_text('请输入手机号').count() > 0
                            has_qr_login = await page.get_by_text('扫码登录').count() > 0
                        except Exception as e:
                            # 如果发生执行上下文被销毁的错误，说明页面可能已经导航
                            # 这通常是登录成功的标志
                            print(f"检测到页面导航，可能已登录成功: {str(e)}")
                            login_successful = True
                            break
                        
                        # 如果两个登录按钮都不存在，则认为已登录成功
                        if not has_phone_login and not has_qr_login:
                            print(f"检测到登录成功! 当前账号: {username}")
                            login_successful = True
                            break
                        
                    except Exception as e:
                        print(f"检查登录状态时出错: {str(e)}")
                        # 出错时继续等待，给用户更多时间完成登录
                        pass
                    
                    # 每分钟提醒一次用户
                    if elapsed_time % 60 == 0 and elapsed_time > 0:
                        minutes = elapsed_time // 60
                        print(f"请尽快完成登录（已等待{minutes}分钟）...")
                    
                    elapsed_time += login_check_interval
                    
                # 检查是否超时
                if not login_successful:
                    print("登录超时：请在5分钟内完成登录操作")
                    await browser.close()
                    return None
                
                # 登录成功后，尝试访问上传页面确认登录状态
                try:
                    # 这里不强制要求访问上传页面成功，因为用户可能已经成功登录
                    # 只需要能获取到cookie即可
                    print(f"已检测到登录成功，正在获取Cookie...")
                    
                    # 尝试访问上传页面，但即使失败也继续进行
                    try:
                        await page.goto("https://creator.douyin.com/creator-micro/content/upload", timeout=8000)
                        # 给页面一些加载时间
                        await page.wait_for_timeout(2000)
                    except Exception as e:
                        print(f"访问上传页面时出错，但继续尝试获取Cookie: {str(e)}")
                        # 不中断流程，继续尝试获取Cookie
                except Exception as e:
                    print(f"验证登录状态时出错: {str(e)}")
                    # 不中断流程，继续尝试获取Cookie
                
                # 获取Cookies
                cookies = await context.cookies()
                
                # 构建Cookie字符串
                cookie_str_parts = []
                for cookie in cookies:
                    # 只保留douyin.com域名的Cookie
                    if ".douyin.com" in cookie['domain'] or "douyin.com" in cookie['domain']:
                        cookie_str_parts.append(f"{cookie['name']}={cookie['value']}")
                
                cookie_str = '; '.join(cookie_str_parts)
                
                # 关闭浏览器
                await browser.close()
                
                return cookie_str
        except Exception as e:
            print(f"使用Playwright登录时发生异常: {str(e)}")
            return None