#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音全能助手 - GUI主入口文件
Author: Loki Wang
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

try:
    from PySide6.QtWidgets import QApplication
    from src.main_window import MainWindow

    def main():
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())

    if __name__ == "__main__":
        main()

except ImportError as e:
    print("错误：缺少必要的GUI库 PySide6")
    print(f"请运行: pip install PySide6")
    print(f"详细错误: {e}")
    sys.exit(1)