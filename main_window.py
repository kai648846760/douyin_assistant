# main_window.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang

import os
import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit, QFileDialog,
                               QMessageBox, QListWidget, QListWidgetItem)
from PySide6.QtCore import QThread, Qt, QObject, Signal

from worker import Worker
from account_manager import AccountManager

class Stream(QObject):
    """用于重定向stdout和stderr到GUI文本框的流对象"""
    message = Signal(str)
    def write(self, text):
        self.message.emit(str(text))
    def flush(self):
        pass

class MainWindow(QMainWindow):
    # 【回滚】只包含我们最终验证成功的、稳定可用的下载模式
    DOWNLOAD_MODES = {
        "主页作品": "post",
        "我的收藏": "favorite",
        "合集作品": "collection",
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
        if msg_type == "success":
            QMessageBox.information(self, "成功", message)
            self.refresh_accounts() # 任务成功后刷新账号列表
        else:
            QMessageBox.critical(self, "失败", message)
        
        # 重新启用所有可能被禁用的按钮
        self.update_cookie_button.setEnabled(True)
        self.download_button.setEnabled(True)
        self.upload_button.setEnabled(True)
        self.thread.quit()
        self.thread.wait()

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
        self.download_url_line.setPlaceholderText("下载主页或合集时，请在此粘贴URL")
        
        path_layout = QHBoxLayout()
        self.download_path_line = QLineEdit()
        self.download_path_line.setPlaceholderText("默认为程序目录下的 downloads 文件夹")
        browse_path_button = QPushButton("浏览...")
        path_layout.addWidget(self.download_path_line)
        path_layout.addWidget(browse_path_button)

        self.download_button = QPushButton("开始下载")
        
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
        layout.addWidget(self.download_button, alignment=Qt.AlignCenter)
        layout.addStretch()
        
        # 连接信号
        self.download_mode_combo.currentTextChanged.connect(self.toggle_download_url_input)
        browse_path_button.clicked.connect(self.browse_download_path)
        self.download_button.clicked.connect(self.start_download)
        
        self.tabs.addTab(tab, "② 视频下载")
        self.toggle_download_url_input(self.download_mode_combo.currentText())

    def create_upload_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.upload_account_combo = QComboBox()
        browse_dir_button = QPushButton("浏览并加载视频...")
        self.video_list_widget = QListWidget()
        self.common_tags_line = QLineEdit()
        self.common_tags_line.setPlaceholderText("为本次上传的所有视频都添加的通用标签, e.g., 原创,教程")
        self.upload_button = QPushButton("开始上传选中的视频")
        
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("选择上传账号 (仅显示上传配置可用的账号):"))
        form_layout.addWidget(self.upload_account_combo)
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
            if acc.get('cookie'):
                status.append("[下载可用]")
                downloadable_accounts.append(acc['username'])
            
            user_data_dir = acc.get('user_data_dir')
            if user_data_dir and os.path.isdir(user_data_dir):
                status.append("[上传可用]")
                uploadable_accounts.append(acc['username'])
            
            self.account_list_text.append(f"用户: {acc.get('username')} | 备注: {acc.get('remark', '无')} | 状态: {' '.join(status) if status else '[配置不完整]'}")
        
        # 更新Cookie的下拉框，显示所有账号
        self.cookie_account_combo.clear()
        self.cookie_account_combo.addItems(all_account_names if all_account_names else ["无账号"])
        
        # 其他下拉框保持过滤逻辑
        self.download_account_combo.clear()
        self.download_account_combo.addItems(downloadable_accounts if downloadable_accounts else ["无可用账号"])
        self.upload_account_combo.clear()
        self.upload_account_combo.addItems(uploadable_accounts if uploadable_accounts else ["无可用账号"])

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
        """根据下载模式决定URL输入框是否可用"""
        mode = self.DOWNLOAD_MODES.get(mode_text)
        self.download_url_line.setEnabled(mode not in ['favorite'])

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
        if mode not in ['favorite'] and not url:
            QMessageBox.warning(self, "警告", "此模式需要填写目标URL！")
            return

        self.download_button.setEnabled(False)
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
        account = self.upload_account_combo.currentText()
        common_tags_str = self.common_tags_line.text()
        selected_videos = [self.video_list_widget.item(i).data(Qt.UserRole) for i in range(self.video_list_widget.count()) if self.video_list_widget.item(i).checkState() == Qt.Checked]

        if not account or account == "无可用账号" or not selected_videos:
            QMessageBox.warning(self, "警告", "请选择有效账号和至少一个视频！")
            return

        self.upload_button.setEnabled(False)
        self.log_output.clear()
        
        tags = [t.strip() for t in common_tags_str.split(',') if t.strip()]
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        
        self.worker.task = lambda: self.worker.run_batch_upload(account, selected_videos, tags)
        self.thread.start()

    def closeEvent(self, event):
        """关闭窗口时确保后台线程也退出"""
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.thread.quit()
        self.thread.wait()
        event.accept()