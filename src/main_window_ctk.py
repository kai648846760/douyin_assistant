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

        # 设置主题和外观
        ctk.set_appearance_mode("dark")  # 暗色主题
        ctk.set_default_color_theme("blue")  # 蓝色主题

        # 设置窗口属性
        self.title("抖音全能助手 by Loki Wang")
        self.geometry("1000x900")
        self.minsize(900, 800)

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
        """创建所有UI组件"""
        # 主容器
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 创建选项卡区域 - 增加高度以确保底部内容可见
        self.tabview = ctk.CTkTabview(main_frame, height=520)
        self.tabview.pack(fill="x", padx=10, pady=(10, 0))

        # 设置选项卡字体
        self.tabview._segmented_button.configure(
            font=ctk.CTkFont(size=13, weight="bold"))

        # 添加选项卡
        self.tab_account = self.tabview.add("① 账号管理")
        self.tab_download = self.tabview.add("② 视频下载")
        self.tab_upload = self.tabview.add("③ 视频上传")

        # 创建各个选项卡的内容
        self.create_account_tab()
        self.create_download_tab()
        self.create_upload_tab()

        # 日志区域 - 固定高度，确保始终可见，增加明显的视觉边界
        log_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=(
            "#2b2b2b", "#1a1a1a"), border_width=2, border_color=("#404040", "#303030"))
        log_frame.pack(fill="x", padx=10, pady=10)

        # 日志内容区域 - 增加高度并添加明显边框
        self.log_text = ctk.CTkTextbox(log_frame, height=180, font=ctk.CTkFont(
            family="Monaco", size=11), corner_radius=8, border_width=1, border_color=("#606060", "#404040"))
        self.log_text.pack(fill="x", padx=8, pady=8)

        # 添加欢迎信息
        welcome_msg = "🎉 欢迎使用抖音全能助手！\n📌 请先在账号管理页面配置您的账号信息\n🚀 然后就可以开始下载或上传视频了\n\n"
        self.log_text.insert("1.0", welcome_msg)

        # 底部状态栏
        status_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        status_frame.pack(fill="x", padx=10, pady=(0, 10))

        # 状态指示器
        status_container = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_container.pack(side="left", fill="x",
                              expand=True, padx=8, pady=6)

        status_indicator = ctk.CTkLabel(
            status_container, text="🟢", font=ctk.CTkFont(size=14))
        status_indicator.pack(side="left")

        self.status_label = ctk.CTkLabel(
            status_container, text="系统就绪", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left", padx=(5, 0))

        # 版本信息和作者
        info_container = ctk.CTkFrame(status_frame, fg_color="transparent")
        info_container.pack(side="right", padx=8, pady=6)

        version_label = ctk.CTkLabel(
            info_container, text="📱 抖音全能助手 v1.0.0", font=ctk.CTkFont(size=10))
        version_label.pack(side="top")

        author_label = ctk.CTkLabel(
            info_container, text="👨‍💻 by Loki Wang", font=ctk.CTkFont(size=10))
        author_label.pack(side="top")

    def create_account_tab(self):
        """创建账号管理选项卡"""
        # 账号列表显示区域
        list_frame = ctk.CTkFrame(self.tab_account)
        list_frame.pack(fill="x", padx=10, pady=(10, 5))

        list_label = ctk.CTkLabel(
            list_frame, text="👥 已配置账号 (状态会实时更新)", font=ctk.CTkFont(size=13, weight="bold"))
        list_label.pack(anchor="w", padx=10, pady=(8, 3))

        self.account_list_text = ctk.CTkTextbox(list_frame, height=100)
        self.account_list_text.pack(fill="x", padx=10, pady=(0, 8))

        # 刷新按钮
        refresh_btn = ctk.CTkButton(
            list_frame, text="🔄 刷新账号列表", command=self.refresh_accounts, height=32)
        refresh_btn.pack(pady=(0, 8))

        # 添加账号区域
        add_frame = ctk.CTkFrame(self.tab_account)
        add_frame.pack(fill="x", padx=10, pady=5)

        add_label = ctk.CTkLabel(
            add_frame, text="➕ 添加新账号", font=ctk.CTkFont(size=13, weight="bold"))
        add_label.pack(anchor="w", padx=10, pady=(8, 3))

        input_frame = ctk.CTkFrame(add_frame)
        input_frame.pack(fill="x", padx=10, pady=(0, 8))

        self.new_account_name = ctk.CTkEntry(
            input_frame, placeholder_text="账号名称 (必填)", height=32)
        self.new_account_name.pack(
            side="left", fill="x", expand=True, padx=(8, 4), pady=6)

        self.new_account_remark = ctk.CTkEntry(
            input_frame, placeholder_text="备注 (可选)", height=32)
        self.new_account_remark.pack(
            side="left", fill="x", expand=True, padx=4, pady=6)

        add_btn = ctk.CTkButton(
            input_frame, text="✅ 添加账号", command=self.add_account, height=32)
        add_btn.pack(side="right", padx=(4, 8), pady=6)

        # Cookie更新区域
        cookie_frame = ctk.CTkFrame(self.tab_account)
        cookie_frame.pack(fill="x", padx=10, pady=5)

        cookie_label = ctk.CTkLabel(
            cookie_frame, text="🍪 更新Cookie", font=ctk.CTkFont(size=13, weight="bold"))
        cookie_label.pack(anchor="w", padx=10, pady=(8, 3))

        cookie_input_frame = ctk.CTkFrame(cookie_frame)
        cookie_input_frame.pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkLabel(cookie_input_frame, text="选择账号:", font=ctk.CTkFont(
            size=11)).pack(side="left", padx=(8, 4), pady=6)
        self.cookie_account_combo = ctk.CTkComboBox(
            cookie_input_frame, values=["无账号"], height=32)
        self.cookie_account_combo.pack(side="left", padx=4, pady=6)

        ctk.CTkLabel(cookie_input_frame, text="选择浏览器:", font=ctk.CTkFont(
            size=11)).pack(side="left", padx=(8, 4), pady=6)
        self.cookie_browser_combo = ctk.CTkComboBox(
            cookie_input_frame, values=['chrome', 'firefox', 'edge', 'opera'], height=32)
        self.cookie_browser_combo.pack(side="left", padx=4, pady=6)

        self.update_cookie_btn = ctk.CTkButton(
            cookie_input_frame, text="🔄 更新选中账号的Cookie", command=self.start_update_cookie, height=32)
        self.update_cookie_btn.pack(side="right", padx=(4, 8), pady=6)

    def create_download_tab(self):
        """创建视频下载选项卡"""
        # 下载配置区域
        config_frame = ctk.CTkFrame(self.tab_download)
        config_frame.pack(fill="x", padx=10, pady=(10, 5))

        config_label = ctk.CTkLabel(
            config_frame, text="⚙️ 下载配置", font=ctk.CTkFont(size=13, weight="bold"))
        config_label.pack(anchor="w", padx=10, pady=(8, 3))

        # 账号选择
        account_frame = ctk.CTkFrame(config_frame)
        account_frame.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(account_frame, text="选择下载账号 (仅显示Cookie可用的账号):", font=ctk.CTkFont(
            size=11)).pack(anchor="w", padx=8, pady=(6, 2))
        self.download_account_combo = ctk.CTkComboBox(
            account_frame, values=["无可用账号"], height=32)
        self.download_account_combo.pack(fill="x", padx=8, pady=(0, 6))

        # 模式选择
        mode_frame = ctk.CTkFrame(config_frame)
        mode_frame.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(mode_frame, text="选择下载模式:", font=ctk.CTkFont(
            size=11)).pack(anchor="w", padx=8, pady=(6, 2))
        self.download_mode_combo = ctk.CTkComboBox(mode_frame, values=list(
            self.DOWNLOAD_MODES.keys()), command=self.toggle_download_url_input, height=32)
        self.download_mode_combo.pack(fill="x", padx=8, pady=(0, 6))

        # URL输入
        url_frame = ctk.CTkFrame(config_frame)
        url_frame.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(url_frame, text="目标URL:", font=ctk.CTkFont(
            size=11)).pack(anchor="w", padx=8, pady=(6, 2))
        self.download_url_entry = ctk.CTkEntry(
            url_frame, placeholder_text="", height=32)
        self.download_url_entry.pack(fill="x", padx=8, pady=(0, 6))

        # 路径选择
        path_frame = ctk.CTkFrame(config_frame)
        path_frame.pack(fill="x", padx=10, pady=(3, 8))

        ctk.CTkLabel(path_frame, text="自定义保存路径 (可选):", font=ctk.CTkFont(
            size=11)).pack(anchor="w", padx=8, pady=(6, 2))

        path_input_frame = ctk.CTkFrame(path_frame)
        path_input_frame.pack(fill="x", padx=8, pady=(0, 6))

        self.download_path_entry = ctk.CTkEntry(
            path_input_frame, placeholder_text="默认为程序目录下的 downloads 文件夹", height=32)
        self.download_path_entry.pack(
            side="left", fill="x", expand=True, padx=(6, 3), pady=4)

        browse_btn = ctk.CTkButton(
            path_input_frame, text="📁 浏览...", command=self.browse_download_path, height=32)
        browse_btn.pack(side="right", padx=(3, 6), pady=4)

        # 下载按钮区域
        button_frame = ctk.CTkFrame(self.tab_download)
        button_frame.pack(fill="x", padx=10, pady=5)

        btn_container = ctk.CTkFrame(button_frame)
        btn_container.pack(pady=12)

        self.download_btn = ctk.CTkButton(
            btn_container, text="⬇️ 开始下载", command=self.start_download, width=130, height=36)
        self.download_btn.pack(side="left", padx=(0, 8))

        self.stop_download_btn = ctk.CTkButton(
            btn_container, text="⏹️ 停止下载", command=self.stop_download, width=130, height=36, state="disabled")
        self.stop_download_btn.pack(side="left")

        # 初始化URL输入框状态
        self.toggle_download_url_input(list(self.DOWNLOAD_MODES.keys())[0])

    def create_upload_tab(self):
        """创建视频上传选项卡 - 大胆优化视频显示区域"""
        # 创建主要内容区域，确保有足够高度显示所有组件包括上传按钮
        content_frame = ctk.CTkFrame(self.tab_upload, height=450)
        content_frame.pack(fill="x", padx=10, pady=5)
        content_frame.pack_propagate(False)

        # 账号选择区域 - 适度压缩
        account_frame = ctk.CTkFrame(content_frame)
        account_frame.pack(fill="x", padx=5, pady=(4, 1))

        account_label = ctk.CTkLabel(
            account_frame, text="👤 选择上传账号 (可多选):", font=ctk.CTkFont(size=11, weight="bold"))
        account_label.pack(anchor="w", padx=5, pady=(3, 2))

        # 账号列表 - 大幅压缩为视频区域让出更多空间
        self.upload_account_frame = ctk.CTkScrollableFrame(
            account_frame)
        self.upload_account_frame.pack(fill="x", padx=8, pady=(0, 2))
        # 绑定鼠标滚轮事件
        self.upload_account_frame.bind_all(
            "<MouseWheel>", self._on_mousewheel_account)
        self.upload_account_frame.bind_all(
            "<Button-4>", self._on_mousewheel_account)
        self.upload_account_frame.bind_all(
            "<Button-5>", self._on_mousewheel_account)

        # 视频选择区域
        video_frame = ctk.CTkFrame(content_frame)
        video_frame.pack(fill="x", padx=8, pady=3)

        # 按钮区域 - 浏览和上传按钮放在同一行
        button_frame = ctk.CTkFrame(video_frame)
        button_frame.pack(fill="x", padx=8, pady=(5, 3))

        browse_btn = ctk.CTkButton(
            button_frame, text="📁 选择视频", command=self.browse_and_list_videos, height=30)
        browse_btn.pack(side="left", padx=(8, 4))

        # 上传按钮与浏览按钮在同一行
        self.upload_btn = ctk.CTkButton(
            button_frame, text="🚀 上传视频", command=self.start_upload, height=30)
        self.upload_btn.pack(side="left", padx=(4, 8))

        video_label = ctk.CTkLabel(
            video_frame, text="🎬 请勾选需要上传的视频 (文件名格式: 标题 #标签1 #标签2.mp4):", font=ctk.CTkFont(size=10))
        video_label.pack(anchor="w", padx=8, pady=2)

        # 视频列表区域 - 大幅扩大高度确保视频列表清晰可见
        self.video_list_frame = ctk.CTkScrollableFrame(video_frame, height=150)
        self.video_list_frame.pack(fill="x", padx=8, pady=(0, 5))
        # 绑定鼠标滚轮事件
        self.video_list_frame.bind_all(
            "<MouseWheel>", self._on_mousewheel_video)
        self.video_list_frame.bind_all("<Button-4>", self._on_mousewheel_video)
        self.video_list_frame.bind_all("<Button-5>", self._on_mousewheel_video)

        # 通用标签区域
        tags_frame = ctk.CTkFrame(content_frame)
        tags_frame.pack(fill="x", padx=8, pady=2)

        tags_label = ctk.CTkLabel(
            tags_frame, text="🏷️ 通用话题标签 (可选):", font=ctk.CTkFont(size=10))
        tags_label.pack(anchor="w", padx=8, pady=(4, 2))

        self.common_tags_entry = ctk.CTkEntry(
            tags_frame, placeholder_text="为本次上传的所有视频都添加的通用标签, e.g., 原创,教程", height=28)
        self.common_tags_entry.pack(fill="x", padx=8, pady=(0, 4))

        # 上传按钮已移动到视频区域与浏览按钮同行

    def append_log(self, text):
        """向日志框追加文本"""
        def update_log():
            self.log_text.insert("end", text)
            self.log_text.see("end")

        # 确保在主线程中更新UI
        if threading.current_thread() == threading.main_thread():
            update_log()
        else:
            self.after(0, update_log)

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

    def _on_mousewheel_account(self, event):
        """账号列表鼠标滚轮事件处理"""
        if hasattr(self, 'upload_account_frame') and self.upload_account_frame.winfo_exists():
            # Windows和macOS的滚轮事件处理
            if event.delta:
                delta = event.delta
            else:
                delta = -40 if event.num == 5 else 40
            self.upload_account_frame._parent_canvas.yview_scroll(
                int(-1 * (delta / 120)), "units")

    def _on_mousewheel_video(self, event):
        """视频列表鼠标滚轮事件处理"""
        if hasattr(self, 'video_list_frame') and self.video_list_frame.winfo_exists():
            # Windows和macOS的滚轮事件处理
            if event.delta:
                delta = event.delta
            else:
                delta = -40 if event.num == 5 else 40
            self.video_list_frame._parent_canvas.yview_scroll(
                int(-1 * (delta / 120)), "units")

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
    """日志重定向器"""

    def __init__(self, callback):
        self.callback = callback

    def write(self, text):
        if text.strip():  # 只有非空文本才输出
            self.callback(text)

    def flush(self):
        pass


if __name__ == "__main__":
    app = MainWindowCTK()
    app.mainloop()
