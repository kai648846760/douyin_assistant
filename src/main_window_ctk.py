# main_window_ctk.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang
# CustomTkinter版本的主窗口，完整保留所有原始功能

from .worker_ctk import WorkerCTK
from .account_manager import AccountManager
from .runtime_config import RuntimeConfig
import os
import sys
import threading
import time
from typing import List, Dict, Optional

import customtkinter as ctk
from tkinter import filedialog, messagebox

# 添加路径以便导入模块
sys.path.insert(0, os.path.dirname(__file__))


class MainWindowCTK(ctk.CTk):
    """使用CustomTkinter重新实现的主窗口，保留所有原始功能"""

    # 下载模式映射，与原版完全一致
    DOWNLOAD_MODES = {
        "主页作品": "post",
        "点赞作品": "like",
        "收藏作品": "collection",  # 需要登录
        "收藏夹作品": "collects",
        "收藏音乐": "music",  # 需要--lyric参数
        "合集作品": "mix",
        "直播下载": "live",
        "单个视频": "one",  # 有Bug，放在最后
    }

    def setup_screen_adaptation(self):
        """设置屏幕适配参数 - 重新设计的等比缩放算法"""
        # 获取屏幕尺寸
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # 基准设计尺寸（以1400x950作为基准）
        base_width = 1400
        base_height = 950
        
        # 计算可用屏幕空间（留出一些边距给系统栏等）
        available_width = screen_width * 0.9  # 留出10%边距
        available_height = screen_height * 0.85  # 留出15%边距给任务栏等
        
        # 计算缩放比例
        width_scale = available_width / base_width
        height_scale = available_height / base_height
        
        # 取较小的缩放比例以保证界面不超出屏幕
        self.scale_factor = min(width_scale, height_scale)
        
        # 限制缩放范围，保证字体不会太小或太大
        if self.scale_factor < 0.8:
            self.scale_factor = 0.8  # 最小不小于0.8倍，保证字体可读
        elif self.scale_factor > 1.3:
            self.scale_factor = 1.3  # 最大不超过1.3倍，避免界面过大
        
        # 计算适配后的窗口尺寸
        self.adaptive_window_width = int(base_width * self.scale_factor)
        self.adaptive_window_height = int(base_height * self.scale_factor)
        
        # 计算最小窗口尺寸
        self.adaptive_min_width = int(1200 * self.scale_factor)
        self.adaptive_min_height = int(850 * self.scale_factor)
        
        # 计算响应式尺寸参数
        self.adaptive_right_panel_width = int(450 * self.scale_factor)
        self.adaptive_padding = max(10, int(15 * self.scale_factor))  # 最小10px
        self.adaptive_content_padding = max(15, int(20 * self.scale_factor))  # 最小15px
        
        # 计算响应式字体大小（重点优化 - 增大字体）
        self.adaptive_title_font = max(26, int(24 * self.scale_factor))  # 最小26px
        self.adaptive_subtitle_font = max(15, int(14 * self.scale_factor))  # 最小15px
        self.adaptive_header_font = max(19, int(18 * self.scale_factor))  # 最小19px
        self.adaptive_normal_font = max(14, int(12 * self.scale_factor))  # 最小14px
        self.adaptive_small_font = max(12, int(11 * self.scale_factor))  # 最小12px
        self.adaptive_tab_font = max(16, int(15 * self.scale_factor))  # 最小16px
        
        # 计算响应式控件尺寸
        self.adaptive_button_height = max(32, int(40 * self.scale_factor))  # 最小32px
        self.adaptive_entry_height = max(30, int(36 * self.scale_factor))  # 最小30px
        self.adaptive_tab_height = max(35, int(45 * self.scale_factor))  # 最小35px
        
        # 输出调试信息
        print(f"🖥️ 屏幕适配信息:")
        print(f"   屏幕尺寸: {screen_width}x{screen_height}")
        print(f"   可用空间: {available_width:.0f}x{available_height:.0f}")
        print(f"   缩放比例: {self.scale_factor:.2f}")
        print(f"   窗口尺寸: {self.adaptive_window_width}x{self.adaptive_window_height}")
        print(f"   标题字体: {self.adaptive_title_font}px")
        print(f"   正文字体: {self.adaptive_normal_font}px")

    def __init__(self):
        super().__init__()

        # 设置主题和外观 - 现代化深色主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # 初始化屏幕适配参数
        self.setup_screen_adaptation()
        
        # 初始化布局更新标志
        self._updating_layout = False

        # 设置窗口属性 - 响应式设计
        self.title("🎬 抖音全能助手 - 现代化版本 by Loki Wang")
        self.geometry(f"{self.adaptive_window_width}x{self.adaptive_window_height}")
        self.minsize(self.adaptive_min_width, self.adaptive_min_height)

        # 设置窗口图标（如果存在）
        try:
            self.iconbitmap("icon.ico")
        except:
            pass

        # 初始化组件
        self.account_manager = AccountManager()
        self.worker = WorkerCTK()

        # 先创建UI组件
        self.create_widgets()
        
        # 然后再设置日志重定向，确保log_text已创建
        self.setup_logging()

        # 初始化数据
        self.refresh_accounts()

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 绑定窗口大小变化事件 - 响应式设计
        self.bind("<Configure>", self.on_window_configure)

    def setup_logging(self):
        """设置日志重定向 - 将系统输出重定向到GUI日志面板"""
        # 启用日志重定向
        sys.stdout = LogRedirector(self.append_log)
        sys.stderr = LogRedirector(self.append_log)

        # 连接worker的信号
        self.worker.progress_callback = self.append_log
        self.worker.finished_callback = self.on_task_finished

    def create_widgets(self):
        """创建现代化左右分栏布局 - 响应式设计"""
        # 主容器 - 使用适配参数
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=self.adaptive_padding, pady=self.adaptive_padding)

        # 创建左右分栏容器
        content_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_container.pack(fill="both", expand=True)

        # 左侧功能区域 - 占用可变宽度
        self.left_panel = ctk.CTkFrame(content_container, corner_radius=15, 
                                      fg_color=("#1a1a1a", "#0d0d0d"), 
                                      border_width=1, border_color=("#404040", "#2a2a2a"))
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, self.adaptive_padding))

        # 右侧信息区域 - 适配宽度
        self.right_panel = ctk.CTkFrame(content_container, width=self.adaptive_right_panel_width, corner_radius=15,
                                       fg_color=("#1a1a1a", "#0d0d0d"),
                                       border_width=1, border_color=("#404040", "#2a2a2a"))
        self.right_panel.pack(side="right", fill="y", padx=(self.adaptive_padding, 0))
        self.right_panel.pack_propagate(False)

        # 创建左侧功能选项卡
        self.create_left_panel()
        
        # 创建右侧信息面板
        self.create_right_panel()

    def create_left_panel(self):
        """创建左侧功能区域 - 响应式设计"""
        # 标题区域
        title_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        title_frame.pack(fill="x", padx=self.adaptive_content_padding, pady=(self.adaptive_content_padding, self.adaptive_padding))
        
        title_label = ctk.CTkLabel(title_frame, text="🎬 抖音全能助手", 
                                  font=ctk.CTkFont(size=self.adaptive_title_font, weight="bold"))
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(title_frame, text="现代化管理界面", 
                                     font=ctk.CTkFont(size=self.adaptive_subtitle_font), 
                                     text_color=("#888888", "#666666"))
        subtitle_label.pack(side="left", padx=(self.adaptive_padding, 0), pady=(5, 0))

        # 创建选项卡区域 - 现代化风格，响应式设计
        self.tabview = ctk.CTkTabview(self.left_panel,
                                     corner_radius=12,
                                     segmented_button_fg_color=("#2d2d2d", "#1f1f1f"),
                                     segmented_button_selected_color=("#1f538d", "#14375e"),
                                     segmented_button_selected_hover_color=("#1f538d", "#14375e"))
        self.tabview.pack(fill="both", expand=True, padx=self.adaptive_content_padding, pady=(self.adaptive_padding, self.adaptive_content_padding))

        # 设置选项卡字体 - 响应式
        self.tabview._segmented_button.configure(
            font=ctk.CTkFont(size=self.adaptive_tab_font, weight="bold"),
            height=self.adaptive_tab_height
        )

        # 添加选项卡 - 使用更直观的图标
        self.tab_account = self.tabview.add("👤 账号管理")
        self.tab_download = self.tabview.add("⬇️ 视频下载")
        self.tab_upload = self.tabview.add("⬆️ 视频上传")

        # 创建各个选项卡的内容
        self.create_account_tab()
        self.create_download_tab()
        self.create_upload_tab()

    def create_right_panel(self):
        """创建右侧信息面板 - 响应式设计"""
        # 系统状态区域
        status_section = ctk.CTkFrame(self.right_panel, corner_radius=12,
                                     fg_color=("#242424", "#1a1a1a"))
        status_section.pack(fill="x", padx=self.adaptive_padding, pady=(self.adaptive_content_padding, self.adaptive_padding))
        
        status_title = ctk.CTkLabel(status_section, text="📊 系统状态",
                                   font=ctk.CTkFont(size=self.adaptive_header_font, weight="bold"))
        status_title.pack(anchor="w", padx=self.adaptive_padding, pady=(12, 8))
        
        # 状态指示器
        status_content = ctk.CTkFrame(status_section, fg_color="transparent")
        status_content.pack(fill="x", padx=self.adaptive_padding, pady=(0, 12))
        
        status_indicator = ctk.CTkLabel(status_content, text="🟢", 
                                       font=ctk.CTkFont(size=self.adaptive_header_font))
        status_indicator.pack(side="left")
        
        self.status_label = ctk.CTkLabel(status_content, text="系统运行正常",
                                        font=ctk.CTkFont(size=self.adaptive_normal_font))
        self.status_label.pack(side="left", padx=(8, 0))
        
        # 实时日志区域
        log_section = ctk.CTkFrame(self.right_panel, corner_radius=12,
                                  fg_color=("#242424", "#1a1a1a"))
        log_section.pack(fill="both", expand=True, padx=self.adaptive_padding, pady=(self.adaptive_padding, self.adaptive_padding))
        
        log_title = ctk.CTkLabel(log_section, text="📝 实时日志",
                                font=ctk.CTkFont(size=self.adaptive_header_font, weight="bold"))
        log_title.pack(anchor="w", padx=self.adaptive_padding, pady=(12, 8))
        
        # 日志内容区域 - 现代化设计和优化显示
        self.log_text = ctk.CTkTextbox(log_section, 
                                      font=ctk.CTkFont(family="JetBrains Mono", size=self.adaptive_small_font),
                                      corner_radius=8,
                                      border_width=1,
                                      border_color=("#404040", "#303030"),
                                      fg_color=("#1e1e1e", "#121212"),
                                      text_color=("#e0e0e0", "#c0c0c0"),
                                      wrap="word")  # 启用自动换行
        self.log_text.pack(fill="both", expand=True, padx=self.adaptive_padding, pady=(0, 12))
        
        # 配置日志文本框的显示属性
        self._configure_log_display()
    
    def _configure_log_display(self):
        """配置日志显示的详细属性"""
        try:
            # 获取底层的tkinter Text组件
            text_widget = self.log_text._textbox
            
            # 配置文本显示属性
            text_widget.configure(
                wrap='word',  # 按单词换行
                spacing1=2,   # 段落上间距
                spacing2=1,   # 行间距
                spacing3=2,   # 段落下间距
                padx=8,       # 左右内边距
                pady=8        # 上下内边距
            )
            
        except Exception as e:
            print(f"配置日志显示错误: {e}")
        
        # 简洁欢迎信息
        welcome_msg = "🎉 抖音全能助手已启动，系统就绪\n\n"
        self.log_text.insert("1.0", welcome_msg)
        self.log_text.see("end")

        # 底部信息区域
        info_section = ctk.CTkFrame(self.right_panel, corner_radius=12,
                                   fg_color=("#242424", "#1a1a1a"))
        info_section.pack(fill="x", padx=self.adaptive_padding, pady=(self.adaptive_padding, self.adaptive_content_padding))
        
        # 版本信息
        version_frame = ctk.CTkFrame(info_section, fg_color="transparent")
        version_frame.pack(fill="x", padx=self.adaptive_padding, pady=12)
        
        version_label = ctk.CTkLabel(version_frame, text="📱 抖音全能助手 v2.0.5",
                                    font=ctk.CTkFont(size=self.adaptive_normal_font, weight="bold"))
        version_label.pack(anchor="w")
        
        author_label = ctk.CTkLabel(version_frame, text="👨‍💻 Powered by Loki Wang",
                                   font=ctk.CTkFont(size=self.adaptive_small_font),
                                   text_color=("#888888", "#666666"))
        author_label.pack(anchor="w", pady=(2, 0))

    def create_account_tab(self):
        """创建账号管理选项卡 - 响应式优化布局"""
        # 主容器 - 使用适配间距
        container = ctk.CTkFrame(self.tab_account, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=self.adaptive_padding, pady=self.adaptive_padding)
        
        # 上半部分：账号列表和操作
        top_section = ctk.CTkFrame(container, corner_radius=12, fg_color=("#2d2d2d", "#1f1f1f"))
        top_section.pack(fill="both", expand=True, pady=(0, self.adaptive_padding))
        
        # 账号列表头部
        list_header = ctk.CTkFrame(top_section, fg_color="transparent")
        list_header.pack(fill="x", padx=self.adaptive_padding, pady=(self.adaptive_padding, self.adaptive_padding))
        
        list_title = ctk.CTkLabel(list_header, text="👥 账号管理中心", 
                                 font=ctk.CTkFont(size=self.adaptive_header_font, weight="bold"))
        list_title.pack(side="left")
        
        refresh_btn = ctk.CTkButton(list_header, text="🔄 刷新", 
                                   command=self.refresh_accounts,
                                   width=int(80 * self.scale_factor), height=int(32 * self.scale_factor),
                                   font=ctk.CTkFont(size=self.adaptive_small_font, weight="bold"))
        refresh_btn.pack(side="right")
        
        # 账号列表内容 - 适配高度
        account_list_height = int(200 * self.scale_factor)
        self.account_list_text = ctk.CTkTextbox(top_section, height=account_list_height, 
                                               font=ctk.CTkFont(family="JetBrains Mono", size=self.adaptive_small_font),
                                               corner_radius=8,
                                               fg_color=("#1e1e1e", "#121212"))
        self.account_list_text.pack(fill="x", padx=self.adaptive_padding, pady=(0, self.adaptive_padding))
        
        # 下半部分：添加账号和Cookie管理 - 分成两列，响应式设计
        bottom_section = ctk.CTkFrame(container, fg_color="transparent")
        bottom_section.pack(fill="x")
        
        # 左列：添加账号
        left_column = ctk.CTkFrame(bottom_section, corner_radius=12, fg_color=("#2d2d2d", "#1f1f1f"))
        left_column.pack(side="left", fill="both", expand=True, padx=(0, self.adaptive_padding // 2))
        
        add_title = ctk.CTkLabel(left_column, text="➕ 添加新账号",
                                font=ctk.CTkFont(size=self.adaptive_header_font - 2, weight="bold"))
        add_title.pack(anchor="w", padx=self.adaptive_padding, pady=(self.adaptive_padding, self.adaptive_padding))
        
        # 账号名称输入
        name_frame = ctk.CTkFrame(left_column, fg_color="transparent")
        name_frame.pack(fill="x", padx=self.adaptive_padding, pady=(0, 8))
        
        ctk.CTkLabel(name_frame, text="账号名称:", font=ctk.CTkFont(size=self.adaptive_normal_font)).pack(anchor="w", pady=(0, 4))
        self.new_account_name = ctk.CTkEntry(name_frame, 
                                            placeholder_text="请输入账号名称",
                                            height=self.adaptive_entry_height, font=ctk.CTkFont(size=self.adaptive_small_font))
        self.new_account_name.pack(fill="x")
        
        # 备注输入
        remark_frame = ctk.CTkFrame(left_column, fg_color="transparent")
        remark_frame.pack(fill="x", padx=self.adaptive_padding, pady=(0, self.adaptive_padding))
        
        ctk.CTkLabel(remark_frame, text="备注信息:", font=ctk.CTkFont(size=self.adaptive_normal_font)).pack(anchor="w", pady=(0, 4))
        self.new_account_remark = ctk.CTkEntry(remark_frame, 
                                              placeholder_text="可选，便于识别账号",
                                              height=self.adaptive_entry_height, font=ctk.CTkFont(size=self.adaptive_small_font))
        self.new_account_remark.pack(fill="x")
        
        # 添加按钮
        add_btn = ctk.CTkButton(left_column, text="✅ 添加账号", 
                               command=self.add_account,
                               height=self.adaptive_button_height, font=ctk.CTkFont(size=self.adaptive_normal_font, weight="bold"),
                               fg_color=("#1f538d", "#14375e"),
                               hover_color=("#2d5aa0", "#1a4168"))
        add_btn.pack(padx=self.adaptive_padding, pady=(0, self.adaptive_padding))
        
        # 右列：Cookie更新
        right_column = ctk.CTkFrame(bottom_section, corner_radius=12, fg_color=("#2d2d2d", "#1f1f1f"))
        right_column.pack(side="right", fill="both", expand=True, padx=(self.adaptive_padding // 2, 0))
        
        cookie_title = ctk.CTkLabel(right_column, text="🍪 Cookie管理",
                                   font=ctk.CTkFont(size=self.adaptive_header_font - 2, weight="bold"))
        cookie_title.pack(anchor="w", padx=self.adaptive_padding, pady=(self.adaptive_padding, self.adaptive_padding))
        
        # 账号选择
        account_frame = ctk.CTkFrame(right_column, fg_color="transparent")
        account_frame.pack(fill="x", padx=self.adaptive_padding, pady=(0, 8))
        
        ctk.CTkLabel(account_frame, text="选择账号:", font=ctk.CTkFont(size=self.adaptive_normal_font)).pack(anchor="w", pady=(0, 4))
        self.cookie_account_combo = ctk.CTkComboBox(account_frame, values=["无账号"],
                                                   height=self.adaptive_entry_height, font=ctk.CTkFont(size=self.adaptive_small_font))
        self.cookie_account_combo.pack(fill="x")
        
        # 更新按钮
        self.update_cookie_btn = ctk.CTkButton(right_column, text="🔄 更新Cookie",
                                              command=self.start_update_cookie,
                                              height=self.adaptive_button_height, font=ctk.CTkFont(size=self.adaptive_normal_font, weight="bold"),
                                              fg_color=("#d97706", "#92400e"),
                                              hover_color=("#f59e0b", "#a16207"))
        self.update_cookie_btn.pack(padx=self.adaptive_padding, pady=(0, self.adaptive_padding))

    def create_download_tab(self):
        """创建视频下载选项卡 - 响应式优化布局"""
        # 主容器 - 使用响应式间距
        container = ctk.CTkFrame(self.tab_download, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=self.adaptive_padding, pady=self.adaptive_padding)
        
        # 上半部分：下载配置区域
        config_section = ctk.CTkFrame(container, corner_radius=12, fg_color=("#2d2d2d", "#1f1f1f"))
        config_section.pack(fill="both", expand=True, pady=(0, self.adaptive_padding))
        
        config_title = ctk.CTkLabel(config_section, text="⚙️ 下载配置中心",
                                   font=ctk.CTkFont(size=self.adaptive_header_font + 1, weight="bold"))
        config_title.pack(anchor="w", padx=self.adaptive_content_padding, pady=(self.adaptive_content_padding, self.adaptive_padding))
        
        # 配置内容主区域
        config_main = ctk.CTkFrame(config_section, fg_color="transparent")
        config_main.pack(fill="both", expand=True, padx=self.adaptive_content_padding, pady=(0, self.adaptive_content_padding))
        
        # 第一行：账号和模式选择
        row1 = ctk.CTkFrame(config_main, fg_color="transparent")
        row1.pack(fill="x", pady=(0, self.adaptive_padding))
        
        # 左列：账号选择
        account_col = ctk.CTkFrame(row1, fg_color="transparent")
        account_col.pack(side="left", fill="both", expand=True, padx=(0, self.adaptive_padding))
        
        ctk.CTkLabel(account_col, text="下载账号：", 
                    font=ctk.CTkFont(size=self.adaptive_normal_font + 1, weight="bold")).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(account_col, text="仅显示Cookie可用的账号", 
                    font=ctk.CTkFont(size=self.adaptive_small_font), text_color=("#888888", "#666666")).pack(anchor="w", pady=(0, 5))
        self.download_account_combo = ctk.CTkComboBox(account_col, values=["无可用账号"],
                                                     height=self.adaptive_button_height, font=ctk.CTkFont(size=self.adaptive_normal_font))
        self.download_account_combo.pack(fill="x")
        
        # 右列：模式选择
        mode_col = ctk.CTkFrame(row1, fg_color="transparent")
        mode_col.pack(side="right", fill="both", expand=True, padx=(self.adaptive_padding, 0))
        
        ctk.CTkLabel(mode_col, text="下载模式：", 
                    font=ctk.CTkFont(size=self.adaptive_normal_font + 1, weight="bold")).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(mode_col, text="选择您需要的下载类型", 
                    font=ctk.CTkFont(size=self.adaptive_small_font), text_color=("#888888", "#666666")).pack(anchor="w", pady=(0, 5))
        self.download_mode_combo = ctk.CTkComboBox(mode_col, values=list(self.DOWNLOAD_MODES.keys()),
                                                  command=self.toggle_download_url_input,
                                                  height=self.adaptive_button_height, font=ctk.CTkFont(size=self.adaptive_normal_font))
        self.download_mode_combo.pack(fill="x")
        
        # 第二行：URL输入
        row2 = ctk.CTkFrame(config_main, fg_color="transparent")
        row2.pack(fill="x", pady=(0, self.adaptive_padding))
        
        ctk.CTkLabel(row2, text="目标URL：", 
                    font=ctk.CTkFont(size=self.adaptive_normal_font + 1, weight="bold")).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(row2, text="请输入对应的抖音链接地址", 
                    font=ctk.CTkFont(size=self.adaptive_small_font), text_color=("#888888", "#666666")).pack(anchor="w", pady=(0, 5))
        self.download_url_entry = ctk.CTkEntry(row2, placeholder_text="",
                                              height=self.adaptive_button_height, font=ctk.CTkFont(size=self.adaptive_normal_font))
        self.download_url_entry.pack(fill="x")
        
        # 第三行：保存路径
        row3 = ctk.CTkFrame(config_main, fg_color="transparent")
        row3.pack(fill="x")
        
        ctk.CTkLabel(row3, text="保存路径：", 
                    font=ctk.CTkFont(size=self.adaptive_normal_font + 1, weight="bold")).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(row3, text="自定义保存位置，留空则使用默认目录", 
                    font=ctk.CTkFont(size=self.adaptive_small_font), text_color=("#888888", "#666666")).pack(anchor="w", pady=(0, 5))
        
        path_frame = ctk.CTkFrame(row3, fg_color="transparent")
        path_frame.pack(fill="x")
        
        self.download_path_entry = ctk.CTkEntry(path_frame,
                                               placeholder_text="默认为程序目录下的 downloads 文件夹",
                                               height=self.adaptive_button_height, font=ctk.CTkFont(size=self.adaptive_normal_font))
        self.download_path_entry.pack(side="left", fill="x", expand=True, padx=(0, self.adaptive_padding))
        
        browse_btn = ctk.CTkButton(path_frame, text="📁 浏览",
                                  command=self.browse_download_path,
                                  width=int(120 * self.scale_factor), height=self.adaptive_button_height,
                                  font=ctk.CTkFont(size=self.adaptive_normal_font, weight="bold"))
        browse_btn.pack(side="right")
        
        # 下半部分：操作按钮区域
        action_section = ctk.CTkFrame(container, corner_radius=12, fg_color=("#2d2d2d", "#1f1f1f"))
        action_section.pack(fill="x")
        
        action_title = ctk.CTkLabel(action_section, text="🚀 操作控制中心",
                                   font=ctk.CTkFont(size=self.adaptive_header_font + 1, weight="bold"))
        action_title.pack(anchor="w", padx=self.adaptive_content_padding, pady=(self.adaptive_content_padding, self.adaptive_padding))
        
        # 按钮区域
        button_container = ctk.CTkFrame(action_section, fg_color="transparent")
        button_container.pack(padx=self.adaptive_content_padding, pady=(0, self.adaptive_content_padding))
        
        download_btn_width = int(180 * self.scale_factor)
        download_btn_height = max(50, int(60 * self.scale_factor))
        
        self.download_btn = ctk.CTkButton(button_container, text="⬇️ 开始下载",
                                         command=self.start_download,
                                         width=download_btn_width, height=download_btn_height,
                                         font=ctk.CTkFont(size=self.adaptive_normal_font + 2, weight="bold"),
                                         fg_color=("#059669", "#047857"),
                                         hover_color=("#10b981", "#059669"))
        self.download_btn.pack(side="left", padx=(0, self.adaptive_padding))
        
        self.stop_download_btn = ctk.CTkButton(button_container, text="⏹️ 停止下载",
                                              command=self.stop_download,
                                              width=download_btn_width, height=download_btn_height,
                                              font=ctk.CTkFont(size=self.adaptive_normal_font + 2, weight="bold"),
                                              state="disabled",
                                              fg_color=("#dc2626", "#b91c1c"),
                                              hover_color=("#ef4444", "#dc2626"))
        self.stop_download_btn.pack(side="left")
        
        # 初始化URL输入框状态
        self.toggle_download_url_input(list(self.DOWNLOAD_MODES.keys())[0])

    def create_upload_tab(self):
        """创建视频上传选项卡 - 彻底重新设计确保底部区域完全可见"""
        # 🎯 新策略：使用固定高度分配，确保底部区域绝对可见
        
        # 主容器 - 不使用expand，避免子组件争抢空间
        container = ctk.CTkFrame(self.tab_upload, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=self.adaptive_padding, pady=self.adaptive_padding)
        
        # 🔥 关键策略：预先计算并分配固定空间
        # 计算可用总高度
        available_height = self.adaptive_window_height - 200  # 预留200px给其他组件
        
        # 固定分配：账号区域30%，视频区域40%，底部区域30%
        account_section_height = max(100, int(available_height * 0.25))  # 25%给账号
        video_section_height = max(120, int(available_height * 0.45))   # 45%给视频
        tags_section_height = max(120, int(available_height * 0.30))    # 30%给底部标签
        
        # 📍 第一部分：账号选择区域 - 严格限制高度
        account_card = ctk.CTkFrame(container, 
                                   corner_radius=12, 
                                   fg_color=("#2d2d2d", "#1f1f1f"),
                                   height=account_section_height)
        account_card.pack(fill="x", pady=(0, 8))  # 不使用expand!
        account_card.pack_propagate(False)  # 🔥 关键：禁止自动调整大小
        
        account_title = ctk.CTkLabel(account_card, text="👤 上传账号",
                                    font=ctk.CTkFont(size=self.adaptive_normal_font + 2, weight="bold"))
        account_title.pack(anchor="w", padx=self.adaptive_padding, pady=(10, 5))
        
        # 极简账号列表 - 固定小高度
        account_list_height = max(40, account_section_height - 60)  # 预留60px给标题和间距
        self.upload_account_frame = ctk.CTkScrollableFrame(account_card, height=account_list_height)
        self.upload_account_frame.pack(fill="x", padx=self.adaptive_padding, pady=(0, 10))
        
        # 📍 第二部分：视频选择区域 - 严格限制高度
        video_card = ctk.CTkFrame(container, 
                                 corner_radius=12, 
                                 fg_color=("#2d2d2d", "#1f1f1f"),
                                 height=video_section_height)
        video_card.pack(fill="x", pady=(0, 8))  # 不使用expand!
        video_card.pack_propagate(False)  # 🔥 关键：禁止自动调整大小
        
        video_title = ctk.CTkLabel(video_card, text="🎥 视频文件",
                                  font=ctk.CTkFont(size=self.adaptive_normal_font + 2, weight="bold"))
        video_title.pack(anchor="w", padx=self.adaptive_padding, pady=(10, 5))
        
        # 紧凑按钮区域
        video_buttons = ctk.CTkFrame(video_card, fg_color="transparent")
        video_buttons.pack(fill="x", padx=self.adaptive_padding, pady=(0, 5))
        
        browse_btn = ctk.CTkButton(video_buttons, text="📁 选择文件夹",
                                  command=self.browse_and_list_videos,
                                  height=32, width=int(140 * self.scale_factor),
                                  font=ctk.CTkFont(size=self.adaptive_small_font, weight="bold"),
                                  fg_color=("#7c3aed", "#5b21b6"),
                                  hover_color=("#8b5cf6", "#6d28d9"))
        browse_btn.pack(side="left", padx=(0, 10))
        
        self.upload_btn = ctk.CTkButton(video_buttons, text="🚀 开始上传",
                                       command=self.start_upload,
                                       height=32, width=int(140 * self.scale_factor),
                                       font=ctk.CTkFont(size=self.adaptive_small_font, weight="bold"),
                                       fg_color=("#059669", "#047857"),
                                       hover_color=("#10b981", "#059669"))
        self.upload_btn.pack(side="left")
        
        # 视频处理选项区域
        process_options_frame = ctk.CTkFrame(video_card, fg_color="transparent")
        process_options_frame.pack(fill="x", padx=self.adaptive_padding, pady=(10, 5))
        
        # 模拟上传模式（dry-run）复选框
        self.dry_run_var = ctk.StringVar(value="1")  # 默认启用dry-run
        dry_run_checkbox = ctk.CTkCheckBox(
            process_options_frame,
            text="🔧 模拟上传模式 (推荐)",
            variable=self.dry_run_var,
            onvalue="1",
            offvalue="0",
            font=ctk.CTkFont(size=self.adaptive_normal_font),
            fg_color=("#3b82f6", "#2563eb"),
            hover_color=("#60a5fa", "#3b82f6"),
            text_color=("#f59e0b", "#fbbf24")
        )
        dry_run_checkbox.pack(side="left", padx=(0, 20), fill="y")
        
        # 启用视频处理的复选框
        self.process_videos_var = ctk.StringVar(value="0")  # 0表示禁用，1表示启用
        process_checkbox = ctk.CTkCheckBox(
            process_options_frame, 
            text="🎞️ 启用视频帧处理", 
            variable=self.process_videos_var, 
            onvalue="1", 
            offvalue="0",
            font=ctk.CTkFont(size=self.adaptive_normal_font)
        )
        process_checkbox.pack(side="left", padx=(0, 20), fill="y")
        
        # 视频帧删除比例滑块
        self.frame_delete_ratio = ctk.DoubleVar(value=0.01)  # 默认删除1%的帧
        ratio_frame = ctk.CTkFrame(process_options_frame, fg_color="transparent")
        ratio_frame.pack(side="left", fill="both", expand=True)
        
        ctk.CTkLabel(ratio_frame, text="📊 帧删除比例: 10%", 
                    font=ctk.CTkFont(size=self.adaptive_normal_font), 
                    text_color=("#555555", "#777777")).pack(anchor="w", pady=(0, 2))
        
        def update_ratio_label(value):
            percentage = int(float(value) * 100)
            ratio_frame.winfo_children()[0].configure(text=f"📊 帧删除比例: {percentage}%")
        
        ratio_slider = ctk.CTkSlider(
            ratio_frame,
            from_=0.01,  # 最小值：1%
            to=0.1,      # 最大值：10%
            number_of_steps=9,  # 9个步长，对应1%-10%的9个级别
            variable=self.frame_delete_ratio,
            command=update_ratio_label
        )
        ratio_slider.pack(fill="x")
        
        # 视频列表 - 固定剩余高度
        video_list_height = max(60, video_section_height - 180)  # 增加预留空间给视频处理选项
        self.video_list_frame = ctk.CTkScrollableFrame(video_card, height=video_list_height)
        self.video_list_frame.pack(fill="x", padx=self.adaptive_padding, pady=(0, 10))
        
        # 📍 第三部分：底部标签区域 - 保持可见
        tags_card = ctk.CTkFrame(container, 
                                corner_radius=12, 
                                fg_color=("#2d2d2d", "#1f1f1f"),
                                height=tags_section_height)
        tags_card.pack(fill="x", side="bottom")  # 🔥 强制底部定位
        tags_card.pack_propagate(False)  # 🔥 关键：禁止被挤压
        
        # 标题
        tags_title = ctk.CTkLabel(tags_card, 
                                 text="🏷️ 通用话题标签",
                                 font=ctk.CTkFont(size=self.adaptive_header_font, weight="bold"))
        tags_title.pack(anchor="w", padx=self.adaptive_padding, pady=(15, 8))
        
        # 标签输入框
        self.common_tags_entry = ctk.CTkEntry(tags_card,
                                             placeholder_text="输入话题标签，如：原创,教程,编程,科技",
                                             height=self.adaptive_entry_height, 
                                             font=ctk.CTkFont(size=self.adaptive_normal_font))
        self.common_tags_entry.pack(fill="x", padx=self.adaptive_padding, pady=(0, 15))

    def append_log(self, text):
        """向日志框追加文本 - 优化显示格式"""
        def update_log():
            try:
                # 处理文本格式
                if text.strip():  # 只处理非空文本
                    # 确保文本以换行结尾，但不重复添加
                    formatted_text = text.rstrip() + '\n'
                    
                    # 在末尾插入文本
                    self.log_text.insert("end", formatted_text)
                    
                    # 自动滚动到最新内容
                    self.log_text.see("end")
                    
                    # 限制日志长度，防止内存溢出
                    self._limit_log_lines()
                    
            except Exception as e:
                # 如果日志显示出错，使用原始标准输出而不是重定向的输出
                sys.__stdout__.write(f"日志显示错误: {e}\n")

        # 确保在主线程中更新UI
        if threading.current_thread() == threading.main_thread():
            update_log()
        else:
            self.after(0, update_log)
    
    def _limit_log_lines(self, max_lines=1000):
        """限制日志行数，防止内存溢出"""
        try:
            # 获取当前内容
            content = self.log_text.get("1.0", "end")
            lines = content.split('\n')
            
            # 如果超过最大行数，删除旧内容
            if len(lines) > max_lines:
                # 保留最后 max_lines - 100 行
                keep_lines = max_lines - 100
                new_content = '\n'.join(lines[-keep_lines:])
                
                # 清除并重新设置内容
                self.log_text.delete("1.0", "end")
                self.log_text.insert("1.0", new_content)
                
                # 滚动到最底部
                self.log_text.see("end")
                
        except Exception as e:
            sys.__stdout__.write(f"日志清理错误: {e}\n")

    def on_task_finished(self, msg_type, message):
        """任务完成回调"""
        def update_ui():
            try:
                if msg_type == "success":
                    messagebox.showinfo("成功", message)
                    self.refresh_accounts()  # 任务成功后刷新账号列表
                elif msg_type == "error":
                    messagebox.showerror("失败", message)
                elif msg_type == "info":
                    # 信息消息，不显示弹窗，只记录到日志
                    self.append_log(f"信息: {message}\n")

                # 重新启用按钮
                self.update_cookie_btn.configure(state="normal")
                self.download_btn.configure(state="normal")
                self.stop_download_btn.configure(state="disabled")
                self.upload_btn.configure(state="normal")

            except Exception as e:
                self.append_log(f"任务完成处理时发生错误: {e}\n")
                # 确保按钮状态正确
                self.update_cookie_btn.configure(state="normal")
                self.download_btn.configure(state="normal")
                self.stop_download_btn.configure(state="disabled")
                self.upload_btn.configure(state="normal")

        # 确保在主线程中更新UI
        if threading.current_thread() == threading.main_thread():
            update_ui()
        else:
            self.after(0, update_ui)

    def refresh_accounts(self):
        """刷新所有账号列表和下拉框"""
        self.account_manager.reload_accounts()
        accounts = self.account_manager.accounts

        # 清空账号列表显示
        self.account_list_text.delete("1.0", "end")

        all_account_names = [acc['username'] for acc in accounts]
        downloadable_accounts = []

        if not accounts:
            self.account_list_text.insert("1.0", "尚未配置任何账号。")
            # 清空所有下拉框
            self.cookie_account_combo.configure(values=["无账号"])
            self.cookie_account_combo.set("无账号")
            self.download_account_combo.configure(values=["无可用账号"])
            self.download_account_combo.set("无可用账号")
            self._update_upload_accounts([])
            return

        # 分析账号状态
        account_status_text = ""
        for acc in accounts:
            status = []

            # 下载状态
            if acc.get('cookie'):
                status.append("[下载可用]")
                downloadable_accounts.append(acc['username'])
            else:
                status.append("[下载需配置]")

            # 上传状态
            user_data_dir = acc.get('user_data_dir')
            if user_data_dir and os.path.isdir(user_data_dir):
                try:
                    if os.listdir(user_data_dir):
                        status.append("[上传已配置]")
                    else:
                        status.append("[上传目录为空]")
                except Exception:
                    status.append("[上传目录为空]")
            else:
                status.append("[上传需配置]")

            account_status_text += f"用户: {acc.get('username')} | 备注: {acc.get('remark', '无')} | 状态: {' '.join(status) if status else '[配置不完整]'}\n"

        self.account_list_text.insert("1.0", account_status_text)

        # 更新Cookie下拉框
        self.cookie_account_combo.configure(
            values=all_account_names if all_account_names else ["无账号"])
        if all_account_names:
            self.cookie_account_combo.set(all_account_names[0])
        else:
            self.cookie_account_combo.set("无账号")

        # 更新下载账号下拉框
        self.download_account_combo.configure(
            values=downloadable_accounts if downloadable_accounts else ["无可用账号"])
        if downloadable_accounts:
            self.download_account_combo.set(downloadable_accounts[0])
        else:
            self.download_account_combo.set("无可用账号")

        # 更新上传账号列表
        self._update_upload_accounts(all_account_names)

    def _update_upload_accounts(self, account_names):
        """更新上传账号多选列表"""
        # 清空现有的复选框
        for widget in self.upload_account_frame.winfo_children():
            widget.destroy()

        self.upload_account_checkboxes = []

        if account_names:
            for username in account_names:
                # 检查是否有上传配置
                account_info = self.account_manager.get_account(username)
                user_data_dir = account_info.get(
                    'user_data_dir') if account_info else None

                if user_data_dir and os.path.isdir(user_data_dir):
                    try:
                        if os.listdir(user_data_dir):
                            display_text = f"{username} [已配置]"
                        else:
                            display_text = f"{username} [目录为空]"
                    except Exception:
                        display_text = f"{username} [目录为空]"
                else:
                    display_text = f"{username} [需配置上传]"

                checkbox = ctk.CTkCheckBox(
                    self.upload_account_frame, text=display_text)
                checkbox.pack(anchor="w", padx=10, pady=2)

                # 存储用户名到checkbox对象
                checkbox.username = username
                self.upload_account_checkboxes.append(checkbox)
        else:
            no_account_label = ctk.CTkLabel(
                self.upload_account_frame, text="无账号")
            no_account_label.pack(anchor="w", padx=10, pady=10)

    def add_account(self):
        """添加新账号"""
        name = self.new_account_name.get().strip()
        remark = self.new_account_remark.get().strip()

        if not name:
            messagebox.showwarning("警告", "账号名称不能为空！")
            return

        self.account_manager.add_account(name, remark)
        messagebox.showinfo("成功", f"账号 '{name}' 已添加。")

        self.new_account_name.delete(0, "end")
        self.new_account_remark.delete(0, "end")
        self.refresh_accounts()

    def start_update_cookie(self):
        """启动更新Cookie的任务"""
        account = self.cookie_account_combo.get()

        if not account or account == "无账号":
            messagebox.showwarning("警告", "请选择一个有效账号！")
            return

        self.update_cookie_btn.configure(state="disabled")
        self.log_text.delete("1.0", "end")

        # 创建进度条
        self.progress_frame = ctk.CTkFrame(self.tab_account)
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="准备更新Cookie...")
        self.progress_label.pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=5)
        self.progress_bar.set(0)

        # 在后台线程中执行任务
        def task():
            def progress_callback(step, total, message):
                # 在主线程中更新UI
                self.after(0, lambda: self.update_progress_ui(step, total, message))
            
            self.worker.run_update_cookie(account, progress_callback)

        threading.Thread(target=task, daemon=True).start()

    def update_progress_ui(self, step, total, message):
        """更新进度条UI（在主线程中调用）"""
        if hasattr(self, 'progress_bar') and hasattr(self, 'progress_label'):
            progress = step / total
            self.progress_bar.set(progress)
            self.progress_label.configure(text=message)
            
            # 如果完成，延迟移除进度条
            if step >= total:
                self.after(2000, self.remove_progress_ui)

    def remove_progress_ui(self):
        """移除进度条UI"""
        if hasattr(self, 'progress_frame'):
            self.progress_frame.destroy()
            delattr(self, 'progress_frame')
            delattr(self, 'progress_bar')
            delattr(self, 'progress_label')

    def browse_download_path(self):
        """浏览下载保存路径"""
        path = filedialog.askdirectory(title="选择保存文件夹")
        if path:
            self.download_path_entry.delete(0, "end")
            self.download_path_entry.insert(0, path)

    def toggle_download_url_input(self, mode_text):
        """根据下载模式决定URL输入框是否可用和提示语"""
        mode = self.DOWNLOAD_MODES.get(mode_text)

        # 所有模式都需要URL输入
        url_required_modes = ['post', 'like', 'collection',
                              'collects', 'mix', 'music', 'one', 'live']
        is_enabled = mode in url_required_modes

        if is_enabled:
            self.download_url_entry.configure(state="normal")
        else:
            self.download_url_entry.configure(state="disabled")

        # 根据模式设置不同的提示语
        placeholders = {
            'post': "请输入用户主页URL (例如: https://www.douyin.com/user/MS4wLjABAAAA...)",
            'like': "请输入用户主页URL (例如: https://www.douyin.com/user/MS4wLjABAAAA...)",
            'collection': "请输入用户主页URL (例如: https://www.douyin.com/user/MS4wLjABAAAA...)",
            'collects': "请输入收藏夹URL (例如: https://www.douyin.com/collection/123456789)",
            'mix': "请输入合集URL或合集中作品URL (例如: https://www.douyin.com/mix/123456789)",
            'music': "请输入音乐作品URL (例如: https://www.douyin.com/music/123456789)",
            'live': "请输入直播间URL (例如: https://live.douyin.com/123456789)",
            'one': "请输入单个视频URL (例如: https://www.douyin.com/video/123456789)"
        }

        placeholder = placeholders.get(mode, "")
        self.download_url_entry.configure(placeholder_text=placeholder)

    def start_download(self):
        """启动下载任务"""
        account = self.download_account_combo.get()
        mode_text = self.download_mode_combo.get()
        mode = self.DOWNLOAD_MODES.get(mode_text)
        url = self.download_url_entry.get().strip()
        path = self.download_path_entry.get().strip()

        if not account or account == "无可用账号":
            messagebox.showwarning("警告", "请选择一个有效账号！")
            return

        # 检查需要URL的模式
        url_required_modes = ['post', 'like', 'collection',
                              'collects', 'mix', 'music', 'one', 'live']
        if mode in url_required_modes and not url:
            messagebox.showwarning("警告", f"模式 '{mode_text}' 需要填写目标URL！")
            return

        self.download_btn.configure(state="disabled")
        self.stop_download_btn.configure(state="normal")
        self.log_text.delete("1.0", "end")

        # 在后台线程中执行任务
        def task():
            self.worker.run_download(account, mode, url, path)

        threading.Thread(target=task, daemon=True).start()

    def browse_and_list_videos(self):
        """浏览并列出视频文件夹中的内容"""
        dir_path = filedialog.askdirectory(title="选择视频文件夹")
        if dir_path:
            # 清空现有的视频列表
            for widget in self.video_list_frame.winfo_children():
                widget.destroy()

            self.video_checkboxes = []

            files = [f for f in os.listdir(dir_path) if f.lower().endswith(
                ('.mp4', '.mov', '.webm', '.avi'))]

            for filename in files:
                checkbox = ctk.CTkCheckBox(
                    self.video_list_frame, text=filename)
                checkbox.pack(anchor="w", padx=10, pady=2)
                checkbox.select()  # 默认选中

                # 存储完整路径
                checkbox.file_path = os.path.join(dir_path, filename)
                self.video_checkboxes.append(checkbox)

            self.append_log(f"已加载目录 '{dir_path}' 中的 {len(files)} 个视频。\n")

    def start_upload(self):
        """启动批量上传任务"""
        # 获取所有选中的账号
        selected_accounts = []
        unconfigured_accounts = []

        for checkbox in self.upload_account_checkboxes:
            if checkbox.get():
                username = checkbox.username
                selected_accounts.append(username)

                # 检查账号配置状态
                account_info = self.account_manager.get_account(username)
                user_data_dir = account_info.get(
                    'user_data_dir') if account_info else None

                # 只有当目录不存在时才算未配置
                if not user_data_dir or not os.path.isdir(user_data_dir):
                    unconfigured_accounts.append(username)

        if not selected_accounts:
            messagebox.showwarning("警告", "请选择至少一个有效账号！")
            return

        # 处理未配置的账号
        configured_accounts = [
            acc for acc in selected_accounts if acc not in unconfigured_accounts]

        if unconfigured_accounts and not configured_accounts:
            # 所有选中的账号都未配置
            unconfigured_str = "、".join(unconfigured_accounts)
            result = messagebox.askyesno(
                "账号配置提醒",
                f"选中的账号都未配置上传功能：{unconfigured_str}\n\n"
                "是否要先配置这些账号的上传设置？"
            )

            if result:
                # 跳转到账号管理页面
                self.tabview.set("① 账号管理")
                messagebox.showinfo("提示",
                                    f"请在账号管理页面为以下账号配置 user_data_dir 路径：\n{unconfigured_str}\n\n"
                                    "配置完成后，请重新尝试上传。")
                return
            else:
                return

        elif unconfigured_accounts and configured_accounts:
            # 部分账号已配置，部分未配置
            unconfigured_str = "、".join(unconfigured_accounts)
            configured_str = "、".join(configured_accounts)
            result = messagebox.askyesno(
                "账号配置提醒",
                f"已配置账号：{configured_str}\n"
                f"未配置账号：{unconfigured_str}\n\n"
                "是否要先配置未配置的账号？\n"
                "(选择'是'将跳转到配置页面，选择'否'将只使用已配置账号上传)"
            )

            if result:
                # 跳转到账号管理页面
                self.tabview.set("① 账号管理")
                messagebox.showinfo("提示",
                                    f"请配置以下账号：\n{unconfigured_str}\n\n"
                                    "配置完成后，请重新尝试上传。")
                return

            # 用户选择跳过未配置的账号，只使用已配置的
            selected_accounts = configured_accounts

        if not selected_accounts:
            messagebox.showwarning("警告", "没有可用的上传账号！")
            return

        # 获取选中的视频
        selected_videos = []
        if hasattr(self, 'video_checkboxes'):
            selected_videos = [
                cb.file_path for cb in self.video_checkboxes if cb.get()]

        if not selected_videos:
            messagebox.showwarning("警告", "请选择至少一个视频！")
            return

        common_tags_str = self.common_tags_entry.get().strip()
        tags = [t.strip() for t in common_tags_str.split(',') if t.strip()]

        self.upload_btn.configure(state="disabled")
        self.log_text.delete("1.0", "end")

        # 获取视频处理相关参数
        process_videos = self.process_videos_var.get() == "1"
        frame_delete_ratio = self.frame_delete_ratio.get()
        dry_run = self.dry_run_var.get() == "1"  # 获取dry-run设置
        
        # 验证运行模式（dry-run/真实上传）
        try:
            resolved_dry_run = RuntimeConfig.resolve_upload_mode(dry_run)
        except PermissionError as exc:
            messagebox.showerror("上传受限", str(exc))
            self.dry_run_var.set("1")
            self.upload_btn.configure(state="normal")
            return

        if resolved_dry_run and not dry_run:
            self.dry_run_var.set("1")
            messagebox.showinfo(
                "已切换为模拟上传",
                "当前环境禁止真实上传，系统已自动切换为模拟模式 (Dry-Run)。")

        dry_run = resolved_dry_run
        
        # 在后台线程中执行任务
        def task():
            self.worker.run_batch_upload(
                selected_accounts, selected_videos, tags,
                process_videos=process_videos,
                frame_delete_ratio=frame_delete_ratio,
                dry_run=dry_run)

        threading.Thread(target=task, daemon=True).start()

    def stop_download(self):
        """停止下载任务"""
        try:
            if self.worker and hasattr(self.worker, 'is_stopping') and not self.worker.is_stopping:
                self.worker.stop_download()
                self.stop_download_btn.configure(state="disabled")
                self.append_log("已发送停止下载请求...\n")
            else:
                self.append_log("没有正在运行的任务或任务已在停止中...\n")
        except Exception as e:
            self.append_log(f"停止下载时发生错误: {e}\n")
            self.stop_download_btn.configure(state="disabled")

    def on_window_configure(self, event):
        """窗口大小变化时的响应式调整 - 实时更新控件，添加防护机制"""
        # 只处理主窗口的大小变化事件
        if event.widget == self:
            try:
                # 防止递归调用的标志
                if hasattr(self, '_updating_layout') and self._updating_layout:
                    return
                
                # 获取当前窗口尺寸
                current_width = event.width
                current_height = event.height
                
                # 与初始设计尺寸比较，计算新的缩放比例
                width_ratio = current_width / 1400  # 基准宽度
                height_ratio = current_height / 950  # 基准高度
                
                # 取较小的比例作为新的缩放因子
                new_scale = min(width_ratio, height_ratio)
                
                # 限制缩放范围，保证字体可读性
                new_scale = max(0.8, min(new_scale, 1.5))  # 增大最大缩放比例
                
                # 即时响应变化，不需要太大变化才触发
                if abs(new_scale - self.scale_factor) > 0.05:  # 提高触发阈值避免频繁更新
                    print(f"🔄 窗口尺寸变化: {current_width}x{current_height}, 新缩放比例: {new_scale:.2f}")
                    
                    # 设置标志防止递归
                    self._updating_layout = True
                    
                    old_scale = self.scale_factor
                    self.scale_factor = new_scale
                    self.update_adaptive_sizes()
                    
                    # 简化的更新逻辑，只更新关键控件
                    self._safe_update_widgets()
                    
                    # 清除标志
                    self._updating_layout = False
                    
            except Exception as e:
                # 静默失败，不影响用户体验
                if hasattr(self, '_updating_layout'):
                    self._updating_layout = False
                print(f"窗口缩放错误: {e}")
    
    def update_adaptive_sizes(self):
        """更新响应式尺寸参数"""
        try:
            # 重新计算各种尺寸参数
            self.adaptive_right_panel_width = int(450 * self.scale_factor)
            self.adaptive_padding = max(10, int(15 * self.scale_factor))
            self.adaptive_content_padding = max(15, int(20 * self.scale_factor))
            
            # 更新字体大小
            self.adaptive_title_font = max(26, int(24 * self.scale_factor))
            self.adaptive_subtitle_font = max(15, int(14 * self.scale_factor))
            self.adaptive_header_font = max(19, int(18 * self.scale_factor))
            self.adaptive_normal_font = max(14, int(12 * self.scale_factor))
            self.adaptive_small_font = max(12, int(11 * self.scale_factor))
            self.adaptive_tab_font = max(16, int(15 * self.scale_factor))
            
            # 更新控件尺寸
            self.adaptive_button_height = max(32, int(40 * self.scale_factor))
            self.adaptive_entry_height = max(30, int(36 * self.scale_factor))
            self.adaptive_tab_height = max(35, int(45 * self.scale_factor))
            
            # 更新右侧面板宽度
            if hasattr(self, 'right_panel'):
                self.right_panel.configure(width=self.adaptive_right_panel_width)
                
        except Exception as e:
            print(f"更新响应式尺寸错误: {e}")
    
    def _safe_update_widgets(self):
        """安全的控件更新方法，避免递归调用"""
        try:
            # 只更新关键控件，避免递归遍历
            
            # 更新右侧面板宽度
            if hasattr(self, 'right_panel'):
                self.right_panel.configure(width=self.adaptive_right_panel_width)
            
            # 更新选项卡字体
            if hasattr(self, 'tabview'):
                try:
                    self.tabview._segmented_button.configure(
                        font=ctk.CTkFont(size=self.adaptive_tab_font, weight="bold"),
                        height=self.adaptive_tab_height
                    )
                except:
                    pass
            
            # 更新第三页特定控件
            self._update_upload_page_widgets()
                
        except Exception as e:
            print(f"安全更新控件错误: {e}")
    
    def _update_upload_page_widgets(self):
        """专门更新第三页的控件尺寸"""
        try:
            # 重新计算空间分配
            available_height = self.adaptive_window_height - 200
            account_section_height = max(100, int(available_height * 0.25))
            video_section_height = max(120, int(available_height * 0.45))
            
            # 更新账号列表高度
            if hasattr(self, 'upload_account_frame'):
                new_height = max(40, account_section_height - 60)
                self.upload_account_frame.configure(height=new_height)
            
            # 更新视频列表高度
            if hasattr(self, 'video_list_frame'):
                new_height = max(60, video_section_height - 90)
                self.video_list_frame.configure(height=new_height)
                
        except Exception as e:
            print(f"更新上传页控件错误: {e}")
    
    # 递归更新方法已被移除以避免无限递归错误
    
    def _update_specific_widgets(self):
        """更新特定控件的尺寸 - 适配新的第三页布局策略"""
        try:
            # 重新计算第三页的空间分配
            available_height = self.adaptive_window_height - 200
            account_section_height = max(100, int(available_height * 0.25))
            video_section_height = max(120, int(available_height * 0.45))
            tags_section_height = max(120, int(available_height * 0.30))
            
            # 更新账号列表高度（与新布局策略保持一致）
            if hasattr(self, 'upload_account_frame'):
                new_height = max(40, account_section_height - 60)
                self.upload_account_frame.configure(height=new_height)
            
            # 更新视频列表高度（与新布局策略保持一致）
            if hasattr(self, 'video_list_frame'):
                new_height = max(60, video_section_height - 90)
                self.video_list_frame.configure(height=new_height)
                
            # 更新下载页面的账号信息列表高度
            if hasattr(self, 'account_list_text'):
                new_height = int(200 * self.scale_factor)
                self.account_list_text.configure(height=new_height)
                
        except Exception as e:
            print(f"更新特定控件错误: {e}")



    def on_closing(self):
        """关闭窗口时的清理工作"""
        # 恢复标准输出
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        # 停止所有任务
        if hasattr(self.worker, 'stop_download'):
            self.worker.stop_download()

        self.destroy()


class LogRedirector:
    """日志重定向器 - 优化版本"""

    def __init__(self, callback):
        self.callback = callback
        self.buffer = []

    def write(self, text):
        if text and text.strip():  # 只处理非空文本
            # 处理特殊字符和格式
            formatted_text = self._format_text(text)
            if formatted_text:
                self.callback(formatted_text)
    
    def _format_text(self, text):
        """格式化文本输出"""
        # 删除多余的空白字符
        text = text.strip()
        
        # 如果文本为空，跳过
        if not text:
            return None
            
        return text

    def flush(self):
        pass


if __name__ == "__main__":
    app = MainWindowCTK()
    app.mainloop()
