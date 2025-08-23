#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright Runtime Hook for PyInstaller
用于确保Playwright在打包环境中正常工作
"""

import os
import sys
from pathlib import Path

def setup_playwright_env():
    """设置Playwright环境变量"""
    try:
        # 检查是否在PyInstaller打包环境中
        if hasattr(sys, '_MEIPASS'):
            # 在打包环境中，设置Playwright相关环境变量
            base_path = Path(sys._MEIPASS)
            
            # 设置Playwright浏览器路径
            playwright_browsers_path = base_path / "playwright" / "browsers"
            if playwright_browsers_path.exists():
                os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(playwright_browsers_path)
            
            # 设置Playwright驱动路径
            playwright_driver_path = base_path / "playwright" / "driver"
            if playwright_driver_path.exists():
                os.environ['PLAYWRIGHT_DRIVER_PATH'] = str(playwright_driver_path)
            
            # 禁用Playwright的下载检查
            os.environ['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD'] = '1'
            
            # 设置用户数据目录
            user_data_dir = Path.home() / ".playwright"
            user_data_dir.mkdir(exist_ok=True)
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(user_data_dir / "browsers")
            
    except Exception as e:
        # 如果设置失败，记录错误但不中断程序
        print(f"Warning: Failed to setup Playwright environment: {e}")

# 在导入时自动执行设置
setup_playwright_env()