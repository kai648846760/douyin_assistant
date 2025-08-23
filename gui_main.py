#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音全能助手 - GUI主入口文件
Author: Loki Wang
"""

import sys
import os
from pathlib import Path

def setup_paths():
    """设置Python路径，支持开发环境和打包环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包环境
        base_path = Path(sys._MEIPASS)
        src_path = base_path / "src"
        config_path = base_path / "config"
    else:
        # 开发环境
        base_path = Path(__file__).parent
        src_path = base_path / "src"
        config_path = base_path / "config"
    
    # 添加路径到sys.path
    for path in [str(base_path), str(src_path), str(config_path)]:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    return base_path, src_path, config_path

def main():
    """主函数"""
    try:
        # 设置路径
        setup_paths()
        
        # 导入必要的库
        from PySide6.QtWidgets import QApplication
        from main_window import MainWindow  # 修复导入路径
        
        # 创建应用
        app = QApplication(sys.argv)
        app.setApplicationName("抖音全能助手")
        app.setApplicationVersion("1.0.0")
        
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        # 运行应用
        sys.exit(app.exec())
        
    except ImportError as e:
        error_msg = f"""
错误：缺少必要的依赖库

详细错误信息：{e}

请确保已正确安装以下依赖：
- PySide6
- requests
- playwright
- rich
- browser-cookie3

可以运行以下命令安装：
pip install -r requirements.txt
        """
        print(error_msg)
        
        # 如果在GUI环境，显示错误对话框
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("启动失败")
            msg.setText("应用启动失败")
            msg.setDetailedText(error_msg)
            msg.exec()
        except:
            pass
        
        sys.exit(1)
    
    except Exception as e:
        error_msg = f"应用启动时发生未预期的错误：{e}"
        print(error_msg)
        
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox
            app = QApplication(sys.argv)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("启动失败")
            msg.setText("应用启动失败")
            msg.setDetailedText(error_msg)
            msg.exec()
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()
