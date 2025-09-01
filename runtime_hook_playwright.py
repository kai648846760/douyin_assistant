import os
import sys
import os
from pathlib import Path
import platform

# 设置Playwright浏览器路径
def setup_playwright_paths():
    # 确定操作系统类型
    system = platform.system().lower()
    
    try:
        # 导入必要的模块用于记录日志
        try:
            from rich.console import Console
            console = Console()
            can_log = True
        except ImportError:
            can_log = False
            
        # 记录基本环境信息
        if can_log:
            console.print(f"[cyan]Runtime Hook: 系统类型: {system}[/cyan]")
            console.print(f"[cyan]Runtime Hook: 是否打包环境: {hasattr(sys, '_MEIPASS')}[/cyan]")
            if hasattr(sys, '_MEIPASS'):
                console.print(f"[cyan]Runtime Hook: MEIPASS路径: {sys._MEIPASS}[/cyan]")
            console.print(f"[cyan]Runtime Hook: 当前Python: {sys.executable}[/cyan]")
        
        # 获取用户主目录
        home_dir = Path.home()
        
        # 为不同操作系统设置默认的Playwright浏览器缓存路径
        if 'darwin' in system:  # macOS
            paths_to_try = [
                home_dir / "Library" / "Caches" / "ms-playwright",
                # 添加额外的备用路径
                Path("/usr/local/share/ms-playwright"),
                Path("/opt/homebrew/share/ms-playwright"),  # Homebrew安装的路径
                Path("/Applications/ms-playwright")  # 额外备用路径
            ]
        elif 'win' in system:  # Windows
            # 使用字符串路径以避免路径解析问题
            paths_to_try = [
                str(home_dir / "AppData" / "Local" / "ms-playwright"),
                os.path.expandvars("%LOCALAPPDATA%\ms-playwright"),
                os.path.expandvars("%PROGRAMFILES%\ms-playwright"),
                os.path.expandvars("%PROGRAMFILES(x86)%\ms-playwright")
            ]
        else:  # Linux
            paths_to_try = [
                home_dir / ".cache" / "ms-playwright",
                Path("/usr/local/share/ms-playwright"),
                Path("/opt/ms-playwright"),
                Path("/var/lib/ms-playwright")
            ]
        
        # 尝试找到第一个存在的路径
        browser_path_set = False
        for browsers_path in paths_to_try:
            # 在Windows上需要特殊处理路径
            if 'win' in system:
                browsers_path_str = browsers_path
            else:
                browsers_path_str = str(browsers_path)
                
            if os.path.exists(browsers_path_str):
                os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_path_str
                browser_path_set = True
                if can_log:
                    console.print(f"[green]Runtime Hook: 找到现有浏览器路径: {browsers_path_str}[/green]")
                break
        
        # 如果没有找到现有路径，设置一个可写的默认路径
        if not browser_path_set:
            # 创建一个应用可写的目录来存储浏览器
            default_browser_path = None
            
            if hasattr(sys, '_MEIPASS'):
                # 在打包环境中，使用用户目录作为浏览器存储位置
                if 'win' in system:
                    # Windows上使用更可靠的路径
                    default_browser_path = os.path.join(str(home_dir), ".playwright_browsers")
                else:
                    default_browser_path = home_dir / ".playwright_browsers"
                    default_browser_path = str(default_browser_path)
                    
                # 确保目录存在
                try:
                    os.makedirs(default_browser_path, exist_ok=True)
                    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = default_browser_path
                    if can_log:
                        console.print(f"[yellow]Runtime Hook: 设置默认浏览器路径: {default_browser_path}[/yellow]")
                except Exception as e:
                    if can_log:
                        console.print(f"[red]Runtime Hook: 无法创建浏览器目录: {e}[/red]")
        
        # 确保不会跳过浏览器下载
        os.environ.pop('PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD', None)
        if can_log:
            console.print(f"[cyan]Runtime Hook: PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD已移除[/cyan]")
        
        # 设置临时目录
        temp_dir = os.environ.get('TEMP', os.environ.get('TMPDIR', '/tmp'))
        os.environ['PLAYWRIGHT_TEMP_DIR'] = temp_dir
        if can_log:
            console.print(f"[cyan]Runtime Hook: 设置PLAYWRIGHT_TEMP_DIR: {temp_dir}[/cyan]")
        
        # 额外的环境变量设置，帮助Playwright找到正确的路径
        os.environ['PLAYWRIGHT_NO_BROWSER_ACCEPT_DOWNLOADS'] = '0'
        
        # 记录最终设置的环境变量
        if can_log:
            console.print(f"[cyan]Runtime Hook: 最终PLAYWRIGHT_BROWSERS_PATH: {os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '未设置')}[/cyan]")
        
    except Exception as e:
        # 记录详细错误信息到临时文件以便调试
        try:
            temp_log = os.path.join(os.environ.get('TEMP', os.environ.get('TMPDIR', '/tmp')), 'playwright_hook_error.log')
            with open(temp_log, 'a') as f:
                f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Error in setup_playwright_paths: {e}\n")
                f.write(f"System: {system}\n")
                f.write(f"Is MEIPASS: {hasattr(sys, '_MEIPASS')}\n")
                if hasattr(sys, '_MEIPASS'):
                    f.write(f"MEIPASS Path: {sys._MEIPASS}\n")
                f.write(f"Python Executable: {sys.executable}\n")
                f.write(f"Home Directory: {str(home_dir)}\n")
                f.write(f"Current Environment Variables:\n")
                for key, value in os.environ.items():
                    if 'PLAYWRIGHT' in key:
                        f.write(f"  {key}: {value}\n")
                f.write("----------------------------------------\n")
        except:
            pass

# 导入time模块用于日志记录
try:
    import time
except ImportError:
    pass

# 在PyInstaller打包环境中运行时执行
if hasattr(sys, '_MEIPASS'):
    setup_playwright_paths()