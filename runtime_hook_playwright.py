import os
import sys
from pathlib import Path

# 设置Playwright浏览器路径
if hasattr(sys, '_MEIPASS'):
    # PyInstaller环境 - 使用系统默认的Playwright浏览器路径
    home_dir = Path.home()
    
    # macOS默认的Playwright浏览器缓存路径
    default_browsers_path = home_dir / "Library" / "Caches" / "ms-playwright"
    
    # 如果默认路径存在，使用它
    if default_browsers_path.exists():
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(default_browsers_path)
    
    # 不跳过浏览器下载，让Playwright自动处理
    # os.environ['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD'] = '1'