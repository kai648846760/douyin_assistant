# main_window_ctk.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang
# CustomTkinter版本的主窗口，完整保留所有原始功能

from .worker_ctk import WorkerCTK
from .account_manager import AccountManager
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

    def __init__(self):
        super().__init__()

        # 设置主题和外观 - 现代化深色主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # 设置窗口属性 - 更大更现代的界面
        self.title("🎬 抖音全能助手 - 现代化版本 by Loki Wang")
        self.geometry("1400x950")
        self.minsize(1200, 850)

        # 设置窗口图标（如果存在）
        try:
            self.iconbitmap("icon.ico")
        except:
            pass

        # 初始化组件
        self.account_manager = AccountManager()
        self.worker = WorkerCTK()
        self.setup_logging()

        # 创建UI
        self.create_widgets()

        # 初始化数据
        self.refresh_accounts()

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_logging(self):
        """设置日志重定向"""
        # 重定向stdout和stderr到日志框
        sys.stdout = LogRedirector(self.append_log)
        sys.stderr = LogRedirector(self.append_log)

        # 连接worker的信号
        self.worker.progress_callback = self.append_log
        self.worker.finished_callback = self.on_task_finished

    def create_widgets(self):
        """创建现代化左右分栏布局"""
        # 主容器 - 现代化设计
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # 创建左右分栏容器
        content_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_container.pack(fill="both", expand=True)

        # 左侧功能区域 - 占用60%宽度
        self.left_panel = ctk.CTkFrame(content_container, corner_radius=15, 
                                      fg_color=("#1a1a1a", "#0d0d0d"), 
                                      border_width=1, border_color=("#404040", "#2a2a2a"))
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # 右侧信息区域 - 固定宽度450px
        self.right_panel = ctk.CTkFrame(content_container, width=450, corner_radius=15,
                                       fg_color=("#1a1a1a", "#0d0d0d"),
                                       border_width=1, border_color=("#404040", "#2a2a2a"))
        self.right_panel.pack(side="right", fill="y", padx=(10, 0))
        self.right_panel.pack_propagate(False)

        # 创建左侧功能选项卡
        self.create_left_panel()
        
        # 创建右侧信息面板
        self.create_right_panel()

    def create_left_panel(self):
        """创建左侧功能区域"""
        # 标题区域
        title_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(title_frame, text="🎬 抖音全能助手", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(title_frame, text="现代化管理界面", 
                                     font=ctk.CTkFont(size=14), 
                                     text_color=("#888888", "#666666"))
        subtitle_label.pack(side="left", padx=(15, 0), pady=(5, 0))

        # 创建选项卡区域 - 现代化风格，去掉固定高度
        self.tabview = ctk.CTkTabview(self.left_panel,
                                     corner_radius=12,
                                     segmented_button_fg_color=("#2d2d2d", "#1f1f1f"),
                                     segmented_button_selected_color=("#1f538d", "#14375e"),
                                     segmented_button_selected_hover_color=("#1f538d", "#14375e"))
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # 设置选项卡字体 - 更现代化
        self.tabview._segmented_button.configure(
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45
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
        """创建右侧信息面板"""
        # 系统状态区域
        status_section = ctk.CTkFrame(self.right_panel, corner_radius=12,
                                     fg_color=("#242424", "#1a1a1a"))
        status_section.pack(fill="x", padx=15, pady=(20, 10))
        
        status_title = ctk.CTkLabel(status_section, text="📊 系统状态",
                                   font=ctk.CTkFont(size=16, weight="bold"))
        status_title.pack(anchor="w", padx=15, pady=(12, 8))
        
        # 状态��态指示器
        status_content = ctk.CTkFrame(status_section, fg_color="transparent")
        status_content.pack(fill="x", padx=15, pady=(0, 12))
        
        status_indicator = ctk.CTkLabel(status_content, text="🟢", 
                                       font=ctk.CTkFont(size=16))
        status_indicator.pack(side="left")
        
        self.status_label = ctk.CTkLabel(status_content, text="系统运行正常",
                                        font=ctk.CTkFont(size=13))
        self.status_label.pack(side="left", padx=(8, 0))
        
        # 实时日志区域
        log_section = ctk.CTkFrame(self.right_panel, corner_radius=12,
                                  fg_color=("#242424", "#1a1a1a"))
        log_section.pack(fill="both", expand=True, padx=15, pady=(10, 10))
        
        log_title = ctk.CTkLabel(log_section, text="📝 实时日志",
                                font=ctk.CTkFont(size=16, weight="bold"))
        log_title.pack(anchor="w", padx=15, pady=(12, 8))
        
        # 日志内容区域 - 现代化设计和优化显示
        self.log_text = ctk.CTkTextbox(log_section, 
                                      font=ctk.CTkFont(family="JetBrains Mono", size=11),
                                      corner_radius=8,
                                      border_width=1,
                                      border_color=("#404040", "#303030"),
                                      fg_color=("#1e1e1e", "#121212"),
                                      text_color=("#e0e0e0", "#c0c0c0"),
                                      wrap="word")  # 启用自动换行
        self.log_text.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        
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
        info_section.pack(fill="x", padx=15, pady=(10, 20))
        
        # 版本信息
        version_frame = ctk.CTkFrame(info_section, fg_color="transparent")
        version_frame.pack(fill="x", padx=15, pady=12)
        
        version_label = ctk.CTkLabel(version_frame, text="📱 抖音全能助手 v2.0.0",
                                    font=ctk.CTkFont(size=12, weight="bold"))
        version_label.pack(anchor="w")
        
        author_label = ctk.CTkLabel(version_frame, text="👨‍💻 Powered by Loki Wang",
                                   font=ctk.CTkFont(size=11),
                                   text_color=("#888888", "#666666"))
        author_label.pack(anchor="w", pady=(2, 0))

    def create_account_tab(self):
        """创建账号管理选项卡 - 优化布局"""
        # 主容器 - 使用垂直分布
        container = ctk.CTkFrame(self.tab_account, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 上半部分：账号列表和操作
        top_section = ctk.CTkFrame(container, corner_radius=12, fg_color=("#2d2d2d", "#1f1f1f"))
        top_section.pack(fill="both", expand=True, pady=(0, 10))
        
        # 账号列表头部
        list_header = ctk.CTkFrame(top_section, fg_color="transparent")
        list_header.pack(fill="x", padx=15, pady=(15, 10))
        
        list_title = ctk.CTkLabel(list_header, text="👥 账号管理中心", 
                                 font=ctk.CTkFont(size=18, weight="bold"))
        list_title.pack(side="left")
        
        refresh_btn = ctk.CTkButton(list_header, text="🔄 刷新", 
                                   command=self.refresh_accounts,
                                   width=80, height=32,
                                   font=ctk.CTkFont(size=11, weight="bold"))
        refresh_btn.pack(side="right")
        
        # 账号列表内容 - 增加高度，充分利用空间
        self.account_list_text = ctk.CTkTextbox(top_section, height=200, 
                                               font=ctk.CTkFont(family="JetBrains Mono", size=11),
                                               corner_radius=8,
                                               fg_color=("#1e1e1e", "#121212"))
        self.account_list_text.pack(fill="x", padx=15, pady=(0, 15))
        
        # 下半部分：添加账号和Cookie管理 - 分成两列
        bottom_section = ctk.CTkFrame(container, fg_color="transparent")
        bottom_section.pack(fill="x")
        
        # 左列：添加账号
        left_column = ctk.CTkFrame(bottom_section, corner_radius=12, fg_color=("#2d2d2d", "#1f1f1f"))
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        add_title = ctk.CTkLabel(left_column, text="➕ 添加新账号",
                                font=ctk.CTkFont(size=16, weight="bold"))
        add_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        # 账号名称输入
        name_frame = ctk.CTkFrame(left_column, fg_color="transparent")
        name_frame.pack(fill="x", padx=15, pady=(0, 8))
        
        ctk.CTkLabel(name_frame, text="账号名称:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 4))
        self.new_account_name = ctk.CTkEntry(name_frame, 
                                            placeholder_text="请输入账号名称",
                                            height=36, font=ctk.CTkFont(size=11))
        self.new_account_name.pack(fill="x")
        
        # 备注输入
        remark_frame = ctk.CTkFrame(left_column, fg_color="transparent")
        remark_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(remark_frame, text="备注信息:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 4))
        self.new_account_remark = ctk.CTkEntry(remark_frame, 
                                              placeholder_text="可选，便于识别账号",
                                              height=36, font=ctk.CTkFont(size=11))
        self.new_account_remark.pack(fill="x")
        
        # 添加按钮
        add_btn = ctk.CTkButton(left_column, text="✅ 添加账号", 
                               command=self.add_account,
                               height=40, font=ctk.CTkFont(size=12, weight="bold"),
                               fg_color=("#1f538d", "#14375e"),
                               hover_color=("#2d5aa0", "#1a4168"))
        add_btn.pack(padx=15, pady=(0, 15))
        
        # 右列：Cookie更新
        right_column = ctk.CTkFrame(bottom_section, corner_radius=12, fg_color=("#2d2d2d", "#1f1f1f"))
        right_column.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        cookie_title = ctk.CTkLabel(right_column, text="🍪 Cookie管理",
                                   font=ctk.CTkFont(size=16, weight="bold"))
        cookie_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        # 账号选择
        account_frame = ctk.CTkFrame(right_column, fg_color="transparent")
        account_frame.pack(fill="x", padx=15, pady=(0, 8))
        
        ctk.CTkLabel(account_frame, text="选择账号:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 4))
        self.cookie_account_combo = ctk.CTkComboBox(account_frame, values=["无账号"],
                                                   height=36, font=ctk.CTkFont(size=11))
        self.cookie_account_combo.pack(fill="x")
        
        # 浏览器选择
        browser_frame = ctk.CTkFrame(right_column, fg_color="transparent")
        browser_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(browser_frame, text="选择浏览器:", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(0, 4))
        self.cookie_browser_combo = ctk.CTkComboBox(browser_frame, 
                                                   values=['chrome', 'firefox', 'edge', 'opera'],
                                                   height=36, font=ctk.CTkFont(size=11))
        self.cookie_browser_combo.pack(fill="x")
        self.cookie_browser_combo.set('chrome')  # 设置默认值
        
        # 更新按钮
        self.update_cookie_btn = ctk.CTkButton(right_column, text="🔄 更新Cookie",
                                              command=self.start_update_cookie,
                                              height=40, font=ctk.CTkFont(size=12, weight="bold"),
                                              fg_color=("#d97706", "#92400e"),
                                              hover_color=("#f59e0b", "#a16207"))
        self.update_cookie_btn.pack(padx=15, pady=(0, 15))

    def create_download_tab(self):
        """创建视频下载选项卡 - 优化布局"""
        # 主容器
        container = ctk.CTkFrame(self.tab_download, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 上半部分：下载配置区域
        config_section = ctk.CTkFrame(container, corner_radius=12, fg_color=("#2d2d2d", "#1f1f1f"))
        config_section.pack(fill="both", expand=True, pady=(0, 10))
        
        config_title = ctk.CTkLabel(config_section, text="⚙️ 下载配置中心",
                                   font=ctk.CTkFont(size=18, weight="bold"))
        config_title.pack(anchor="w", padx=20, pady=(20, 15))
        
        # 配置内容主区域
        config_main = ctk.CTkFrame(config_section, fg_color="transparent")
        config_main.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 第一行：账号和模式选择
        row1 = ctk.CTkFrame(config_main, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 15))
        
        # 左列：账号选择
        account_col = ctk.CTkFrame(row1, fg_color="transparent")
        account_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(account_col, text="下载账号：", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(account_col, text="仅显示Cookie可用的账号", 
                    font=ctk.CTkFont(size=11), text_color=("#888888", "#666666")).pack(anchor="w", pady=(0, 5))
        self.download_account_combo = ctk.CTkComboBox(account_col, values=["无可用账号"],
                                                     height=40, font=ctk.CTkFont(size=12))
        self.download_account_combo.pack(fill="x")
        
        # 右列：模式选择
        mode_col = ctk.CTkFrame(row1, fg_color="transparent")
        mode_col.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(mode_col, text="下载模式：", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(mode_col, text="选择您需要的下载类型", 
                    font=ctk.CTkFont(size=11), text_color=("#888888", "#666666")).pack(anchor="w", pady=(0, 5))
        self.download_mode_combo = ctk.CTkComboBox(mode_col, values=list(self.DOWNLOAD_MODES.keys()),
                                                  command=self.toggle_download_url_input,
                                                  height=40, font=ctk.CTkFont(size=12))
        self.download_mode_combo.pack(fill="x")
        
        # 第二行：URL输入
        row2 = ctk.CTkFrame(config_main, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(row2, text="目标URL：", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(row2, text="请输入对应的抖音链接地址", 
                    font=ctk.CTkFont(size=11), text_color=("#888888", "#666666")).pack(anchor="w", pady=(0, 5))
        self.download_url_entry = ctk.CTkEntry(row2, placeholder_text="",
                                              height=40, font=ctk.CTkFont(size=12))
        self.download_url_entry.pack(fill="x")
        
        # 第三行：保存路径
        row3 = ctk.CTkFrame(config_main, fg_color="transparent")
        row3.pack(fill="x")
        
        ctk.CTkLabel(row3, text="保存路径：", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 8))
        ctk.CTkLabel(row3, text="自定义保存位置，留空则使用默认目录", 
                    font=ctk.CTkFont(size=11), text_color=("#888888", "#666666")).pack(anchor="w", pady=(0, 5))
        
        path_frame = ctk.CTkFrame(row3, fg_color="transparent")
        path_frame.pack(fill="x")
        
        self.download_path_entry = ctk.CTkEntry(path_frame,
                                               placeholder_text="默认为程序目录下的 downloads 文件夹",
                                               height=40, font=ctk.CTkFont(size=12))
        self.download_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(path_frame, text="📁 浏览",
                                  command=self.browse_download_path,
                                  width=100, height=40,
                                  font=ctk.CTkFont(size=12, weight="bold"))
        browse_btn.pack(side="right")
        
        # 下半部分：操作按钮区域
        action_section = ctk.CTkFrame(container, corner_radius=12, fg_color=("#2d2d2d", "#1f1f1f"))
        action_section.pack(fill="x")
        
        action_title = ctk.CTkLabel(action_section, text="🚀 操作控制中心",
                                   font=ctk.CTkFont(size=18, weight="bold"))
        action_title.pack(anchor="w", padx=20, pady=(20, 15))
        
        # 按钮区域
        button_container = ctk.CTkFrame(action_section, fg_color="transparent")
        button_container.pack(padx=20, pady=(0, 20))
        
        self.download_btn = ctk.CTkButton(button_container, text="⬇️ 开始下载",
                                         command=self.start_download,
                                         width=160, height=50,
                                         font=ctk.CTkFont(size=16, weight="bold"),
                                         fg_color=("#059669", "#047857"),
                                         hover_color=("#10b981", "#059669"))
        self.download_btn.pack(side="left", padx=(0, 15))
        
        self.stop_download_btn = ctk.CTkButton(button_container, text="⏹️ 停止下载",
                                              command=self.stop_download,
                                              width=160, height=50,
                                              font=ctk.CTkFont(size=16, weight="bold"),
                                              state="disabled",
                                              fg_color=("#dc2626", "#b91c1c"),
                                              hover_color=("#ef4444", "#dc2626"))
        self.stop_download_btn.pack(side="left")
        
        # 初始化URL输入框状态
        self.toggle_download_url_input(list(self.DOWNLOAD_MODES.keys())[0])

    def create_upload_tab(self):
        """创建视频上传选项卡 - 紧凑设计"""
        # 主容器 - 去掉滚动
        container = ctk.CTkFrame(self.tab_upload, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 账号选择卡片 - 紧凑设计
        account_card = ctk.CTkFrame(container, corner_radius=12, fg_color=("#2d2d2d", "#1f1f1f"))
        account_card.pack(fill="x", pady=(0, 10))
        
        account_title = ctk.CTkLabel(account_card, text="👤 上传账号选择",
                                    font=ctk.CTkFont(size=16, weight="bold"))
        account_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # 账号列表区域 - 减少高度
        self.upload_account_frame = ctk.CTkScrollableFrame(account_card, height=70)
        self.upload_account_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # 视频选择卡片 - 紧凑设计
        video_card = ctk.CTkFrame(container, corner_radius=12, fg_color=("#2d2d2d", "#1f1f1f"))
        video_card.pack(fill="x", pady=(0, 10))
        
        video_title = ctk.CTkLabel(video_card, text="🎥 视频文件选择",
                                  font=ctk.CTkFont(size=16, weight="bold"))
        video_title.pack(anchor="w", padx=15, pady=(10, 8))
        
        # 按钮区域 - 紧凑设计
        video_buttons = ctk.CTkFrame(video_card, fg_color="transparent")
        video_buttons.pack(fill="x", padx=15, pady=(0, 8))
        
        browse_btn = ctk.CTkButton(video_buttons, text="📁 选择文件夹",
                                  command=self.browse_and_list_videos,
                                  height=32, font=ctk.CTkFont(size=11, weight="bold"),
                                  fg_color=("#7c3aed", "#5b21b6"),
                                  hover_color=("#8b5cf6", "#6d28d9"),
                                  width=120)
        browse_btn.pack(side="left", padx=(0, 8))
        
        self.upload_btn = ctk.CTkButton(video_buttons, text="🚀 开始上传",
                                       command=self.start_upload,
                                       height=32, font=ctk.CTkFont(size=11, weight="bold"),
                                       fg_color=("#059669", "#047857"),
                                       hover_color=("#10b981", "#059669"),
                                       width=120)
        self.upload_btn.pack(side="left")
        
        # 视频列表区域 - 减少高度
        self.video_list_frame = ctk.CTkScrollableFrame(video_card, height=120)
        self.video_list_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # 通用标签卡片 - 紧凑设计
        tags_card = ctk.CTkFrame(container, corner_radius=12, fg_color=("#2d2d2d", "#1f1f1f"))
        tags_card.pack(fill="x")
        
        tags_title = ctk.CTkLabel(tags_card, text="🏷️ 通用话题标签",
                                 font=ctk.CTkFont(size=16, weight="bold"))
        tags_title.pack(anchor="w", padx=15, pady=(10, 8))
        
        self.common_tags_entry = ctk.CTkEntry(tags_card,
                                             placeholder_text="例如：原创,教程,编程,科技",
                                             height=32, font=ctk.CTkFont(size=11))
        self.common_tags_entry.pack(fill="x", padx=15, pady=(0, 10))

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
                # 如果日志显示出错，不要影响主程序
                print(f"日志显示错误: {e}")

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
            print(f"日志清理错误: {e}")

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
        browser = self.cookie_browser_combo.get()

        if not account or account == "无账号":
            messagebox.showwarning("警告", "请选择一个有效账号！")
            return

        self.update_cookie_btn.configure(state="disabled")
        self.log_text.delete("1.0", "end")

        # 在后台线程中执行任务
        def task():
            self.worker.run_update_cookie(account, browser)

        threading.Thread(target=task, daemon=True).start()

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

        # 在后台线程中执行任务
        def task():
            self.worker.run_batch_upload(
                selected_accounts, selected_videos, tags)

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
