# gui.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang

import sys
from PySide6.QtWidgets import QApplication
from .main_window import MainWindow

if __name__ == '__main__':
    # 为了在打包后也能找到 Playwright 的浏览器，可能需要设置环境变量
    # os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"
    
    app = QApplication(sys.argv)
    
    # 设置一个现代化的样式
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    # 确保程序退出时，后台线程也能被正确关闭
    app.aboutToQuit.connect(window.thread.quit)
    
    sys.exit(app.exec())