import sys
import os
from pathlib import Path
import platform

# 设置Playwright浏览器路径
def setup_playwright_paths():
    # 确定操作系统类型
    system = platform.system().lower()
    
    try:
        # 获取用户主目录
        home_dir = Path.home()
        
        # 为不同操作系统设置默认的Playwright浏览器缓存路径
        if 'darwin' in system:  # macOS
            paths_to_try = [
                home_dir / "Library" / "Caches" / "ms-playwright",
                # 添加额外的备用路径
                Path("/usr/local/share/ms-playwright")
            ]
        elif 'win' in system:  # Windows
            paths_to_try = [
                home_dir / "AppData" / "Local" / "ms-playwright",
                Path(r"C:\Program Files\ms-playwright")
            ]
        else:  # Linux
            paths_to_try = [
                home_dir / ".cache" / "ms-playwright",
                Path("/usr/local/share/ms-playwright"),
                Path("/opt/ms-playwright")
            ]
        
        # 尝试找到第一个存在的路径
        for browsers_path in paths_to_try:
            if browsers_path.exists():
                os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(browsers_path)
                break
            
        # 设置为不跳过浏览器下载，让Playwright自动处理
        # os.environ['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD'] = '1'
        
    except Exception as e:
        # 静默处理错误，避免程序崩溃
        pass

# 在PyInstaller打包环境中运行时执行
if hasattr(sys, '_MEIPASS'):
    setup_playwright_paths()