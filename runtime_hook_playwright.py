"""
PyInstaller runtime hook for Playwright
修复Playwright在打包应用中的浏览器路径问题
"""
import os
import sys
from pathlib import Path

def setup_playwright_paths():
    """设置Playwright在打包环境中的路径"""
    try:
        # 检查是否在PyInstaller打包环境中
        if hasattr(sys, '_MEIPASS'):
            # 打包环境
            base_path = Path(sys._MEIPASS)
            
            # 设置Playwright相关环境变量
            os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH', str(base_path / '_playwright_browsers'))
            os.environ.setdefault('PLAYWRIGHT_DRIVER_PATH', str(base_path / '_playwright_driver'))
            
            # 如果需要，可以设置为使用系统浏览器
            if not os.path.exists(os.environ['PLAYWRIGHT_BROWSERS_PATH']):
                # 尝试使用系统Chrome路径（如果可用）
                chrome_paths = [
                    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS
                    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',   # Windows
                    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',  # Windows x86
                    '/usr/bin/google-chrome',  # Linux
                    '/usr/bin/chromium-browser',  # Linux Chromium
                ]
                
                for chrome_path in chrome_paths:
                    if os.path.exists(chrome_path):
                        os.environ['PLAYWRIGHT_CHROME_EXECUTABLE'] = chrome_path
                        break
        
    except Exception as e:
        # 如果设置失败，不要阻止应用启动
        print(f"Warning: Failed to setup Playwright paths: {e}")

# 在模块导入时执行设置
setup_playwright_paths()
