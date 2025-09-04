#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Loki Wang
# CustomTkinter版本的GUI入口文件

import os
import sys

# 路径设置 - 支持开发环境和PyInstaller打包环境
if getattr(sys, 'frozen', False):
    # PyInstaller打包后的环境
    base_path = sys._MEIPASS
else:
    # 开发环境
    base_path = os.path.dirname(os.path.abspath(__file__))

# 添加src目录到Python路径
src_path = os.path.join(base_path, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def main():
    """主函数"""
    try:
        # 导入CustomTkinter主窗口
        from src.main_window_ctk import MainWindowCTK
        import traceback
        
        print("开始初始化主窗口...")
        # 创建并运行应用
        app = MainWindowCTK()
        print("主窗口初始化完成，开始主循环...")
        app.mainloop()
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("\n请确保已安装必要的依赖:")
        print("pip install requests playwright rich browser-cookie3 customtkinter")
        print("\n注意: 不再需要安装PySide6")
        sys.exit(1)
    except Exception as e:
        print(f"启动应用时发生错误: {e}")
        print("\n错误详情:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()