#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音全能助手 - 主入口文件
Author: Loki Wang
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# 导入主应用程序
from src.main import main

if __name__ == "__main__":
    main()