# main_window.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang

import os
import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit, QFileDialog,
                               QMessageBox, QListWidget, QListWidgetItem)
from PySide6.QtCore import QThread, Qt, QObject, Signal

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from .worker import Worker
from .account_manager import AccountManager

class Stream(QObject):
    """用于重定向stdout和stderr到GUI文本框的流对象"""
    message = Signal(str)
    def write(self, text):
        self.message.emit(str(text))
    def flush(self):
        pass

class MainWindow(QMainWindow):
    # 【修正】使用与F2项目一致的模式名称，按用户期望的顺序排列
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
        self.setWindowTitle("抖音全能助手 by Loki Wang")
        self.setGeometry(100, 100, 850, 700)
        
        self.account_manager = AccountManager()
        self.setup_worker_thread()
        self.setup_logging()

        # --- 创建主界面UI ---
        self.tabs = QTabWidget()
        
        # 创建所有Tab页和它们包含的UI控件
        self.create_account_tab()
        self.create_download_tab()
        self.create_upload_tab()

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4; font-family: 'Monaco', 'Courier New';")
        
        # --- 主布局 ---
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(QLabel("任务实时日志:"))
        main_layout.addWidget(self.log_output)
        self.setCentralWidget(main_widget)
        
        # 在所有控件都创建完毕后，最后再调用一次刷新，为它们填充初始数据
        self.refresh_accounts()

    def setup_logging(self):
        """将stdout和stderr重定向到GUI的日志框"""
        self.log_stream = Stream()
        sys.stdout = self.log_stream
        sys.stderr = self.log_stream
        self.log_stream.message.connect(self.append_log)

    def setup_worker_thread(self):
        """创建并设置后台工作线程"""
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.worker.progress.connect(self.append_log)
        self.worker.finished.connect(self.on_task_finished)
        self.thread.started.connect(self.worker.run)

    def append_log(self, text):
        """向日志框安全地追加文本，并自动滚动到底部"""
        self.log_output.insertPlainText(text)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def on_task_finished(self, msg_type, message):
        """任务完成后的回调函数"""
        try:
            if msg_type == "success":
                QMessageBox.information(self, "成功", message)
                self.refresh_accounts() # 任务成功后刷新账号列表
            elif msg_type == "error":
                QMessageBox.critical(self, "失败", message)
            elif msg_type == "info":
                # 信息消息，不显示弹窗，只记录到日志
                self.append_log(f"信息: {message}")

            # 重新启用所有可能被禁用的按钮
            self.update_cookie_button.setEnabled(True)
            self.download_button.setEnabled(True)
            self.stop_download_button.setEnabled(False)
            self.upload_button.setEnabled(True)

            # 安全地终止线程
            if self.thread.isRunning():
                self.thread.quit()
                if not self.thread.wait(5000):  # 等待最多5秒
                    self.append_log("警告: 线程未能正常终止")
                    self.thread.terminate()  # 强制终止

        except Exception as e:
            self.append_log(f"任务完成处理时发生错误: {e}")
            # 确保按钮状态正确
            self.update_cookie_button.setEnabled(True)
            self.download_button.setEnabled(True)
            self.stop_download_button.setEnabled(False)
            self.upload_button.setEnabled(True)

    # ----------------- Tab页创建函数 -----------------

    def create_account_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.account_list_text = QTextEdit()
        self.account_list_text.setReadOnly(True)
        refresh_button = QPushButton("刷新账号列表")
        
        add_layout = QHBoxLayout()
        self.new_account_name = QLineEdit()
        self.new_account_name.setPlaceholderText("账号名称 (必填)")
        self.new_account_remark = QLineEdit()
        self.new_account_remark.setPlaceholderText("备注 (可选)")
        add_button = QPushButton("添加账号")
        add_layout.addWidget(self.new_account_name)
        add_layout.addWidget(self.new_account_remark)
        add_layout.addWidget(add_button)

        cookie_layout = QHBoxLayout()
        self.cookie_account_combo = QComboBox()
        self.cookie_browser_combo = QComboBox()
        self.cookie_browser_combo.addItems(['chrome', 'firefox', 'edge', 'opera'])
        self.update_cookie_button = QPushButton("更新选中账号的Cookie")
        cookie_layout.addStretch()
        cookie_layout.addWidget(QLabel("选择账号:"))
        cookie_layout.addWidget(self.cookie_account_combo)
        cookie_layout.addWidget(QLabel("选择浏览器:"))
        cookie_layout.addWidget(self.cookie_browser_combo)
        cookie_layout.addWidget(self.update_cookie_button)
        cookie_layout.addStretch()

        layout.addWidget(QLabel("已配置账号 (状态会实时更新):"))
        layout.addWidget(self.account_list_text)
        layout.addWidget(refresh_button)
        layout.addLayout(add_layout)
        layout.addLayout(cookie_layout)
        
        # 连接信号
        refresh_button.clicked.connect(self.refresh_accounts)
        add_button.clicked.connect(self.add_account)
        self.update_cookie_button.clicked.connect(self.start_update_cookie)
        self.tabs.addTab(tab, "① 账号管理")

    def create_download_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.download_account_combo = QComboBox()
        self.download_mode_combo = QComboBox()
        self.download_mode_combo.addItems(self.DOWNLOAD_MODES.keys())
        self.download_url_line = QLineEdit()
        # URL提示语会根据选择的模式动态设置
        self.download_url_line.setPlaceholderText("")
        
        path_layout = QHBoxLayout()
        self.download_path_line = QLineEdit()
        self.download_path_line.setPlaceholderText("默认为程序目录下的 downloads 文件夹")
        browse_path_button = QPushButton("浏览...")
        path_layout.addWidget(self.download_path_line)
        path_layout.addWidget(browse_path_button)

        self.download_button = QPushButton("开始下载")
        self.stop_download_button = QPushButton("停止下载")
        self.stop_download_button.setEnabled(False)

        # 下载按钮布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.stop_download_button)

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("选择下载账号 (仅显示Cookie可用的账号):"))
        form_layout.addWidget(self.download_account_combo)
        form_layout.addWidget(QLabel("选择下载模式:"))
        form_layout.addWidget(self.download_mode_combo)
        form_layout.addWidget(QLabel("目标URL:"))
        form_layout.addWidget(self.download_url_line)
        form_layout.addWidget(QLabel("自定义保存路径 (可选):"))
        form_layout.addLayout(path_layout)

        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        # 连接信号
        self.download_mode_combo.currentTextChanged.connect(self.toggle_download_url_input)
        browse_path_button.clicked.connect(self.browse_download_path)
        self.download_button.clicked.connect(self.start_download)
        self.stop_download_button.clicked.connect(self.stop_download)
        
        self.tabs.addTab(tab, "② 视频下载")
        self.toggle_download_url_input(self.download_mode_combo.currentText())

    def create_upload_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.upload_account_list = QListWidget()
        self.upload_account_list.setSelectionMode(QListWidget.MultiSelection)  # 允许多选
        browse_dir_button = QPushButton("浏览并加载视频...")
        self.video_list_widget = QListWidget()
        self.common_tags_line = QLineEdit()
        self.common_tags_line.setPlaceholderText("为本次上传的所有视频都添加的通用标签, e.g., 原创,教程")
        self.upload_button = QPushButton("开始上传选中的视频")

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("选择上传账号 (可多选，显示配置中的所有账号):"))
        form_layout.addWidget(self.upload_account_list)
        form_layout.addWidget(browse_dir_button)
        form_layout.addWidget(QLabel("请勾选需要上传的视频 (文件名格式: 标题 #标签1 #标签2.mp4):"))
        form_layout.addWidget(self.video_list_widget)
        form_layout.addWidget(QLabel("通用话题标签 (可选):"))
        form_layout.addWidget(self.common_tags_line)

        layout.addLayout(form_layout)
        layout.addWidget(self.upload_button, alignment=Qt.AlignCenter)

        # 连接信号
        browse_dir_button.clicked.connect(self.browse_and_list_videos)
        self.upload_button.clicked.connect(self.start_upload)

        self.tabs.addTab(tab, "③ 视频上传")


    # ----------------- 逻辑和槽函数 -----------------

    def refresh_accounts(self):
        """刷新所有账号列表和下拉框"""
        self.account_manager.reload_accounts()
        accounts = self.account_manager.accounts
        self.account_list_text.clear()
        
        all_account_names = [acc['username'] for acc in accounts]
        downloadable_accounts = []
        uploadable_accounts = []
        
        if not accounts:
            self.account_list_text.setText("尚未配置任何账号。")
            # 清空所有下拉框
            self.cookie_account_combo.clear()
            self.download_account_combo.clear()
            self.upload_account_combo.clear()
            return

        for acc in accounts:
            status = []

            # 下载状态
            if acc.get('cookie'):
                status.append("[下载可用]")
                downloadable_accounts.append(acc['username'])
            else:
                status.append("[下载需配置]")

            # 上传状态 - 使用新的判断逻辑
            user_data_dir = acc.get('user_data_dir')
            if user_data_dir and os.path.isdir(user_data_dir):
                try:
                    if os.listdir(user_data_dir):
                        status.append("[上传已配置]")
                    else:
                        status.append("[上传目录为空]")
                    uploadable_accounts.append(acc['username'])
                except Exception:
                    status.append("[上传目录为空]")
                    uploadable_accounts.append(acc['username'])
            else:
                status.append("[上传需配置]")

            self.account_list_text.append(f"用户: {acc.get('username')} | 备注: {acc.get('remark', '无')} | 状态: {' '.join(status) if status else '[配置不完整]'}")
        
        # 更新Cookie的下拉框，显示所有账号
        self.cookie_account_combo.clear()
        self.cookie_account_combo.addItems(all_account_names if all_account_names else ["无账号"])
        
        # 其他下拉框保持过滤逻辑
        self.download_account_combo.clear()
        self.download_account_combo.addItems(downloadable_accounts if downloadable_accounts else ["无可用账号"])

        # 更新上传账号多选列表，显示所有账号（包括没有上传配置的）
        self.upload_account_list.clear()
        if all_account_names:
            for username in all_account_names:
                # 检查是否有上传配置，添加状态提示
                account_info = self.account_manager.get_account(username)
                user_data_dir = account_info.get('user_data_dir') if account_info else None

                if user_data_dir and os.path.isdir(user_data_dir):
                    # 检查目录是否为空
                    try:
                        if os.listdir(user_data_dir):
                            display_text = f"{username} [已配置]"
                        else:
                            display_text = f"{username} [目录为空]"
                    except Exception:
                        display_text = f"{username} [目录为空]"
                else:
                    display_text = f"{username} [需配置上传]"

                item = QListWidgetItem(display_text)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)  # 默认不选中
                # 使用setData存储用户名，注意要确保username是字符串
                if isinstance(username, str):
                    item.setData(Qt.UserRole, username)
                self.upload_account_list.addItem(item)
        else:
            item = QListWidgetItem("无账号")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)  # 禁用项
            self.upload_account_list.addItem(item)

    def add_account(self):
        """添加新账号"""
        name = self.new_account_name.text()
        remark = self.new_account_remark.text()
        if not name:
            QMessageBox.warning(self, "警告", "账号名称不能为空！")
            return
        self.account_manager.add_account(name, remark)
        QMessageBox.information(self, "成功", f"账号 '{name}' 已添加。")
        self.new_account_name.clear()
        self.new_account_remark.clear()
        self.refresh_accounts()

    def start_update_cookie(self):
        """启动更新Cookie的任务"""
        account = self.cookie_account_combo.currentText()
        browser = self.cookie_browser_combo.currentText()
        if not account or account == "无账号":
            QMessageBox.warning(self, "警告", "请选择一个有效账号！")
            return

        self.update_cookie_button.setEnabled(False)
        self.log_output.clear()
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        
        self.worker.task = lambda: self.worker.run_update_cookie(account, browser)
        self.thread.start()
        
    def browse_download_path(self):
        """浏览下载保存路径"""
        path = QFileDialog.getExistingDirectory(self, "选择保存文件夹")
        if path:
            self.download_path_line.setText(path)

    def toggle_download_url_input(self, mode_text):
        """根据下载模式决定URL输入框是否可用和提示语"""
        mode = self.DOWNLOAD_MODES.get(mode_text)
        # 所有模式都需要URL输入 (用于获取sec_user_id创建文件夹)
        url_required_modes = ['post', 'like', 'collection', 'collects', 'mix', 'music', 'one', 'live']
        is_enabled = mode in url_required_modes
        self.download_url_line.setEnabled(is_enabled)

        # 根据模式设置不同的提示语
        if mode == 'post':
            placeholder = "请输入用户主页URL (例如: https://www.douyin.com/user/MS4wLjABAAAA...)"
        elif mode == 'like':
            placeholder = "请输入用户主页URL (例如: https://www.douyin.com/user/MS4wLjABAAAA...)"
        elif mode == 'collection':
            placeholder = "请输入用户主页URL (例如: https://www.douyin.com/user/MS4wLjABAAAA...)"
        elif mode == 'collects':
            placeholder = "请输入收藏夹URL (例如: https://www.douyin.com/collection/123456789)"
        elif mode == 'mix':
            placeholder = "请输入合集URL或合集中作品URL (例如: https://www.douyin.com/mix/123456789)"
        elif mode == 'music':
            placeholder = "请输入音乐作品URL (例如: https://www.douyin.com/music/123456789)"
        elif mode == 'live':
            placeholder = "请输入直播间URL (例如: https://live.douyin.com/123456789)"
        elif mode == 'one':
            placeholder = "请输入单个视频URL (例如: https://www.douyin.com/video/123456789)"
        else:
            placeholder = ""

        self.download_url_line.setPlaceholderText(placeholder)

    def start_download(self):
        """启动下载任务"""
        account = self.download_account_combo.currentText()
        mode_text = self.download_mode_combo.currentText()
        mode = self.DOWNLOAD_MODES.get(mode_text)
        url = self.download_url_line.text()
        path = self.download_path_line.text()

        if not account or account == "无可用账号":
            QMessageBox.warning(self, "警告", "请选择一个有效账号！")
            return

        # 检查需要URL的模式 (所有模式都需要URL用于获取sec_user_id)
        url_required_modes = ['post', 'like', 'collection', 'collects', 'mix', 'music', 'one', 'live']
        if mode in url_required_modes and not url:
            QMessageBox.warning(self, "警告", f"模式 '{mode_text}' 需要填写目标URL！")
            return

        self.download_button.setEnabled(False)
        self.stop_download_button.setEnabled(True)
        self.log_output.clear()
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        self.worker.task = lambda: self.worker.run_download(account, mode, url, path)
        self.thread.start()

    def browse_and_list_videos(self):
        """浏览并列出视频文件夹中的内容"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择视频文件夹")
        if dir_path:
            self.video_list_widget.clear()
            files = [f for f in os.listdir(dir_path) if f.lower().endswith(('.mp4', '.mov', '.webm', '.avi'))]
            for filename in files:
                item = QListWidgetItem(filename)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked) # 默认全部选中
                item.setData(Qt.UserRole, os.path.join(dir_path, filename)) # 存储完整路径
                self.video_list_widget.addItem(item)
            self.append_log(f"已加载目录 '{dir_path}' 中的 {len(files)} 个视频。")

    def start_upload(self):
        """启动批量上传任务"""
        # 获取所有选中的账号
        selected_accounts = []
        unconfigured_accounts = []

        for i in range(self.upload_account_list.count()):
            item = self.upload_account_list.item(i)
            if item and item.checkState() == Qt.Checked:
                username = item.data(Qt.UserRole)
                if username and isinstance(username, str) and username != "无账号":
                    selected_accounts.append(username)

                    # 检查账号配置状态
                    account_info = self.account_manager.get_account(username)
                    user_data_dir = account_info.get('user_data_dir') if account_info else None

                    # 只有当目录不存在时才算未配置
                    if not user_data_dir or not os.path.isdir(user_data_dir):
                        unconfigured_accounts.append(username)
                    # 如果目录存在但为空，不算未配置，允许继续操作

        if not selected_accounts:
            QMessageBox.warning(self, "警告", "请选择至少一个有效账号！")
            return

        # 处理未配置的账号
        configured_accounts = [acc for acc in selected_accounts if acc not in unconfigured_accounts]

        if unconfigured_accounts and not configured_accounts:
            # 所有选中的账号都未配置
            unconfigured_str = "、".join(unconfigured_accounts)
            reply = QMessageBox.question(
                self, "账号配置提醒",
                f"选中的账号都未配置上传功能：{unconfigured_str}\n\n"
                "是否要先配置这些账号的上传设置？",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # 跳转到账号管理页面
                self.tabs.setCurrentIndex(0)  # 切换到账号管理Tab
                QMessageBox.information(self, "提示",
                    f"请在账号管理页面为以下账号配置 user_data_dir 路径：\n{unconfigured_str}\n\n"
                    "配置完成后，请重新尝试上传。")
                return
            else:
                return  # 用户选择不配置，直接返回

        elif unconfigured_accounts and configured_accounts:
            # 部分账号已配置，部分未配置
            unconfigured_str = "、".join(unconfigured_accounts)
            configured_str = "、".join(configured_accounts)
            reply = QMessageBox.question(
                self, "账号配置提醒",
                f"已配置账号：{configured_str}\n"
                f"未配置账号：{unconfigured_str}\n\n"
                "是否要先配置未配置的账号？\n"
                "(选择'是'将跳转到配置页面，选择'否'将只使用已配置账号上传)",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # 跳转到账号管理页面
                self.tabs.setCurrentIndex(0)
                QMessageBox.information(self, "提示",
                    f"请配置以下账号：\n{unconfigured_str}\n\n"
                    "配置完成后，请重新尝试上传。")
                return

            # 用户选择跳过未配置的账号，只使用已配置的
            selected_accounts = configured_accounts

        # 继续使用已配置的账号进行上传

        if not selected_accounts:
            QMessageBox.warning(self, "警告", "没有可用的上传账号！")
            return

        common_tags_str = self.common_tags_line.text()
        selected_videos = [self.video_list_widget.item(i).data(Qt.UserRole) for i in range(self.video_list_widget.count()) if self.video_list_widget.item(i).checkState() == Qt.Checked]

        if not selected_videos:
            QMessageBox.warning(self, "警告", "请选择至少一个视频！")
            return

        self.upload_button.setEnabled(False)
        self.log_output.clear()

        tags = [t.strip() for t in common_tags_str.split(',') if t.strip()]
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        # 传递多个账号进行批量上传
        self.worker.task = lambda: self.worker.run_batch_upload(selected_accounts, selected_videos, tags)
        self.thread.start()

    def stop_download(self):
        """停止下载任务"""
        try:
            if self.worker and hasattr(self.worker, 'is_stopping') and not self.worker.is_stopping:
                self.worker.stop_download()
                self.stop_download_button.setEnabled(False)
                self.append_log("已发送停止下载请求...")
            else:
                self.append_log("没有正在运行的任务或任务已在停止中...")
        except Exception as e:
            self.append_log(f"停止下载时发生错误: {e}")
            self.stop_download_button.setEnabled(False)

    def closeEvent(self, event):
        """关闭窗口时确保后台线程也退出"""
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.thread.quit()
        self.thread.wait()
        event.accept()