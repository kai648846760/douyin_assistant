# uploader.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang

import os
import time
import subprocess
import sys
import platform
from playwright.sync_api import sync_playwright, Browser, Page, Playwright, TimeoutError as PlaywrightTimeoutError
from rich.console import Console

console = Console()

def ensure_playwright_browsers():
    """确保Playwright浏览器已安装，特别优化了PyInstaller打包环境下的兼容性"""
    try:
        console.print(f"[cyan]开始检查Playwright浏览器状态...[/cyan]")
        console.print(f"[cyan]当前环境: {'打包环境 (MEIPASS)' if hasattr(sys, '_MEIPASS') else '开发环境'}[/cyan]")
        console.print(f"[cyan]Python解释器: {sys.executable}[/cyan]")
        
        # 确保不会跳过浏览器下载
        os.environ.pop('PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD', None)
        console.print(f"[cyan]PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD: {'已移除' if 'PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD' not in os.environ else os.environ['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD']}[/cyan]")
        
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
        try:
            with sync_playwright() as p:
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
        except Exception as e:
            console.print(f"[yellow]Playwright初始化异常: {e}[/yellow]")
        
        # 如果浏览器不可用，尝试安装
        console.print("[yellow]检测到Playwright浏览器未安装或不可用，正在自动安装...[/yellow]")
        
        # 尝试多种安装方法
        install_methods = [
            {"name": "标准Playwright安装", "method": _install_playwright_standard},
            {"name": "备用Playwright安装", "method": _install_playwright_alternative},
            {"name": "系统Python安装", "method": _install_playwright_system_python}
        ]
        
        for method_info in install_methods:
            try:
                console.print(f"[cyan]尝试{method_info['name']}...[/cyan]")
                success = method_info['method']()
                if success:
                    console.print(f"[green]{method_info['name']}成功！[/green]")
                    # 安装成功后，验证浏览器是否可用
                    try:
                        with sync_playwright() as p:
                            browser_path = p.chromium.executable_path
                            if os.path.exists(browser_path):
                                return True
                            else:
                                console.print(f"[red]安装成功但浏览器文件不存在: {browser_path}[/red]")
                                continue
                    except Exception as e:
                        console.print(f"[red]安装成功但验证失败: {e}[/red]")
                        continue
            except Exception as e:
                console.print(f"[red]{method_info['name']}失败: {e}[/red]")
                continue
        
        # 如果所有安装方法都失败
        console.print("[red]所有安装方法都失败了！[/red]")
        console.print("[yellow]提示: 请尝试手动运行 'python -m playwright install chromium' 命令[/yellow]")
        
        # 作为最后的备选，直接使用系统Chrome浏览器（如果有）
        if _has_system_chrome():
            console.print("[green]检测到系统已安装Chrome浏览器，可以直接使用！[/green]")
            return True
        
        return False
        
    except Exception as e:
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


def _install_playwright_standard():
    """标准的Playwright安装方法"""
    # 构建安装命令参数
    install_args = ["-m", "playwright", "install", "chromium"]
    
    # 根据不同环境选择Python解释器
    if hasattr(sys, '_MEIPASS'):
        console.print("[cyan]在打包环境中，寻找合适的Python解释器...[/cyan]")
        
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
    
    for line in process.stdout:
        # 检查是否包含进度信息
        if "downloading" in line.lower() or "extracting" in line.lower():
            progress_index = (progress_index + 1) % len(progress_chars)
            console.print(f"  [cyan]{progress_chars[progress_index]} {line.strip()}[/cyan]", end="\r")
        else:
            console.print(f"  [gray]{line.strip()}[/gray]")
    
    # 等待进程完成并获取返回码
    process.wait(timeout=300)
    
    return process.returncode == 0


def _install_playwright_alternative():
    """备用的Playwright安装方法，使用pip install playwright"""
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
    
    # 显示安装进度
    for line in process.stdout:
        console.print(f"  [gray]{line.strip()}[/gray]")
    
    process.wait(timeout=300)
    
    return process.returncode == 0


def _install_playwright_system_python():
    """使用系统Python安装Playwright"""
    # 获取系统Python路径
    system_python_paths = []
    
    if platform.system() == 'Windows':
        system_python_paths = [
            'python',
            'py',
            os.path.expandvars('%LOCALAPPDATA%\Programs\Python\Python39\python.exe'),
            os.path.expandvars('%LOCALAPPDATA%\Programs\Python\Python310\python.exe'),
            os.path.expandvars('%LOCALAPPDATA%\Programs\Python\Python311\python.exe'),
            os.path.expandvars('%LOCALAPPDATA%\Programs\Python\Python312\python.exe'),
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
            console.print(f"[cyan]尝试使用系统Python: {python_exe}[/cyan]")
            
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
                return True
        except Exception as e:
            console.print(f"[red]使用{python_exe}失败: {e}[/red]")
            continue
    
    return False


def _has_system_chrome():
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
            os.path.expandvars('%PROGRAMFILES%\Google\Chrome\Application\chrome.exe'),
            os.path.expandvars('%PROGRAMFILES(x86)%\Google\Chrome\Application\chrome.exe')
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
            # 如果安装失败，尝试使用系统安装的Playwright
            console.print("[yellow]尝试使用系统中已安装的Playwright...[/yellow]")
            # 尝试直接启动，不依赖ensure_playwright_browsers的返回值
            try:
                # 跳过安装检查，直接尝试启动
                pass
            except Exception:
                raise RuntimeError("无法安装或使用Playwright浏览器")
            
        # 在启动前再次检查环境变量
        if hasattr(sys, '_MEIPASS'):
            console.print(f"[cyan]当前打包环境: {sys._MEIPASS}[/cyan]")
            console.print(f"[cyan]PLAYWRIGHT_BROWSERS_PATH: {os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '未设置')}[/cyan]")
        
        # 尝试启动Playwright
        try:
            self.playwright = sync_playwright().start()
        except Exception as e:
            console.print(f"[red]无法启动Playwright: {e}[/red]")
            # 尝试获取系统中已安装的Playwright路径
            try:
                # 尝试使用系统Python的Playwright
                console.print("[yellow]尝试使用系统中已安装的Playwright...[/yellow]")
                # 这是一个备选方案，直接尝试重新导入
                from playwright.sync_api import sync_playwright
                self.playwright = sync_playwright().start()
            except Exception as e2:
                raise RuntimeError(f"无法初始化Playwright: {e2}")
        
        console.print("[green]正在启动浏览器...[/green]")
        
        # 准备多种启动配置，逐步降级尝试
        launch_configs = [
            # 配置1: 标准配置
            {
                'user_data_dir': self.user_data_dir,
                'headless': False,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',  # 解决权限问题
                    '--disable-dev-shm-usage',  # 解决内存问题
                    '--disable-gpu',  # 避免GPU相关问题
                    '--disable-extensions',  # 禁用扩展
                    '--start-maximized'  # 最大化窗口
                ]
            },
            # 配置2: 使用系统Chrome（如果有）
            {
                'user_data_dir': self.user_data_dir,
                'headless': False,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            },
            # 配置3: Headless模式作为最后的备选
            {
                'user_data_dir': self.user_data_dir,
                'headless': True,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            }
        ]
        
        # 检查是否有系统Chrome可用
        system_chrome_paths = []
        if platform.system() == 'Darwin':  # macOS
            system_chrome_paths = [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
            ]
        elif platform.system() == 'Windows':  # Windows
            system_chrome_paths = [
                os.path.expandvars('%PROGRAMFILES%\Google\Chrome\Application\chrome.exe'),
                os.path.expandvars('%PROGRAMFILES(x86)%\Google\Chrome\Application\chrome.exe')
            ]
        else:  # Linux
            system_chrome_paths = [
                '/usr/bin/google-chrome',
                '/usr/bin/chromium-browser'
            ]
        
        # 设置系统Chrome路径（如果有）
        for chrome_path in system_chrome_paths:
            if os.path.exists(chrome_path):
                launch_configs[1]['executable_path'] = chrome_path
                console.print(f"[cyan]找到系统Chrome浏览器: {chrome_path}[/cyan]")
                break
        
        # 优先使用环境变量中指定的浏览器路径
        if 'PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH' in os.environ:
            browser_exe_path = os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH']
            if os.path.exists(browser_exe_path):
                launch_configs[0]['executable_path'] = browser_exe_path
                console.print(f"[blue]使用环境变量指定的浏览器路径: {browser_exe_path}[/blue]")
        
        # 尝试启动浏览器，使用多种配置逐步降级
        self.browser = None
        for config_idx, config in enumerate(launch_configs):
            try:
                config_name = ['标准配置', '系统Chrome', 'Headless模式'][config_idx]
                console.print(f"[yellow]尝试使用{config_name}启动浏览器...[/yellow]")
                self.browser = self.playwright.chromium.launch_persistent_context(**config)
                console.print("[green]浏览器启动成功！[/green]")
                break  # 成功启动，跳出循环
            except Exception as e:
                console.print(f"[red]使用{config_name}启动浏览器失败: {e}[/red]")
                # 尝试清理环境变量后重试
                if config_idx == 0 and 'PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH' in os.environ:
                    console.print("[yellow]尝试移除浏览器路径环境变量后重试...[/yellow]")
                    del os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH']
        
        # 如果所有配置都失败，抛出异常
        if not self.browser:
            error_msg = "无法使用任何配置启动浏览器"
            console.print(f"[red]{error_msg}[/red]")
            # 尝试手动创建用户数据目录
            os.makedirs(self.user_data_dir, exist_ok=True)
            console.print(f"[yellow]已确保用户数据目录存在: {self.user_data_dir}[/yellow]")
            raise RuntimeError(error_msg)
        
        # 获取页面对象
        page = self.browser.pages[0] if self.browser.pages else self.browser.new_page()
        
        # 导航到上传页面
        upload_url = "https://creator.douyin.com/creator-micro/content/upload"
        home_url_fragment = "/creator-micro/home"
        
        try:
            console.print(f"[cyan]导航到上传页面: {upload_url}[/cyan]")
            page.goto(upload_url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            console.print(f"[red]导航到上传页面失败: {e}[/red]")
            # 尝试备用URL
            console.print("[yellow]尝试使用备用URL...[/yellow]")
            page.goto("https://creator.douyin.com", wait_until="domcontentloaded", timeout=60000)
        
        # 检查登录状态
        console.print("[blue]正在检查登录状态或等待您登录...[/blue]")
        max_wait_time = 300  # 最多等待5分钟
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                if page.get_by_role('button', name='上传视频').count() > 0:
                    console.print("[green]‘上传视频’按钮已找到，您已登录！[/green]")
                    break
                if home_url_fragment in page.url:
                    console.print(f"[green]检测到已跳转到创作者主页，登录成功！[/green]")
                    break
                # 额外检查：如果出现登录页面的特定元素，也认为需要登录
                if "login" in page.url.lower() or page.locator('input[name="phone"]').count() > 0:
                    console.print("[yellow]检测到需要登录，请扫码或输入账号密码登录...[/yellow]")
            except Exception as e:
                console.print(f"[red]检查登录状态时出错: {e}[/red]")
            
            # 显示剩余等待时间
            elapsed = int(time.time() - start_time)
            remaining = max_wait_time - elapsed
            console.print(f"  [-] 未检测到登录成功信号，等待您登录，{remaining}秒后超时...", end="\r")
            time.sleep(5)
        
        if time.time() - start_time >= max_wait_time:
            console.print("[red]登录等待超时，请检查网络连接或手动登录...[/red]")
            # 不抛出异常，让用户有机会手动操作
        
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