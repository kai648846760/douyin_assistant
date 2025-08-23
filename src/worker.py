
# worker.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang

import os
import time
from PySide6.QtCore import QObject, Signal
from account_manager import AccountManager
from uploader import Uploader
from downloader import Downloader

class Worker(QObject):
    finished = Signal(str, str)
    progress = Signal(str)

    def __init__(self):
        super().__init__()
        self.account_manager = AccountManager()
        self.task = None
        self.is_stopping = False
        self.current_thread = None

    def run(self):
        if self.task:
            try:
                self.is_stopping = False
                self.task()
            except Exception as e:
                if not self.is_stopping:
                    self.finished.emit("error", f"任务执行时发生异常: {e}")

    def stop_download(self):
        """停止当前下载任务"""
        self.is_stopping = True
        # 如果downloader存在，设置停止标志
        if hasattr(self, '_current_downloader') and self._current_downloader:
            self._current_downloader._stop_requested = True
        self.finished.emit("info", "正在停止下载任务...")

    def run_update_cookie(self, account, browser_name):
        try:
            self.account_manager.update_cookie_from_browser(account, browser_name)
            self.finished.emit("success", f"账号 '{account}' 的Cookie更新尝试已完成。")
        except Exception as e: self.finished.emit("error", f"更新Cookie时发生异常: {e}")

    def run_download(self, account, mode, url, download_path):
        """【核心修正】支持所有下载模式"""
        account_info = self.account_manager.get_account(account)
        if not account_info or not account_info.get('cookie'):
            self.finished.emit("error", f"账号 '{account}' 不存在或Cookie未配置。"); return

        downloader = Downloader(account_info['cookie'], download_path)
        self._current_downloader = downloader  # 保存引用以便停止

        try:
            # 检查是否停止
            if self.is_stopping:
                self.finished.emit("info", "下载任务已被用户取消")
                return

            # 根据mode调用不同的下载方法
            if mode == 'one':
                downloader.download_from_url(url)
            elif mode == 'post':
                downloader.download_from_post(url)
            elif mode == 'like':
                downloader.download_from_like(url)
            elif mode == 'collection':
                downloader.download_from_favorite()  # collection模式需要登录，使用favorite方法
            elif mode == 'collects':
                downloader.download_from_collects(url)
            elif mode == 'mix':
                downloader.download_from_mix(url)
            elif mode == 'music':
                downloader.download_from_music(url)
            elif mode == 'live':
                downloader.download_live(url)

            # 再次检查是否停止
            if not self.is_stopping:
                self.finished.emit("success", f"下载任务已完成。")

        except Exception as e:
            if not self.is_stopping:
                self.finished.emit("error", f"下载过程中发生错误: {e}")
            else:
                self.finished.emit("info", f"下载任务被取消: {e}")

    def run_upload(self, account, video_path, title, tags):
        """执行单个视频上传任务"""
        account_info = self.account_manager.get_account(account)
        if not account_info:
            self.finished.emit("error", f"账号 '{account}' 不存在。"); return
        
        uploader = Uploader(account_info['user_data_dir'])
        success = uploader.upload_video(video_path, title, tags)
        
        if success: self.finished.emit("success", f"视频 '{os.path.basename(video_path)}' 上传成功！")
        else: self.finished.emit("error", "上传失败，详情请查看日志。")

    def run_batch_upload(self, accounts, video_list, common_tags):
        """执行批量上传任务 (支持多账号)"""
        # 确保accounts是列表格式
        if isinstance(accounts, str):
            accounts = [accounts]

        if not accounts:
            self.finished.emit("error", "未选择任何有效账号。"); return

        total_success, total_fail = 0, 0

        # 对每个账号执行上传任务
        for account in accounts:
            account_info = self.account_manager.get_account(account)
            if not account_info:
                self.progress.emit(f"账号 '{account}' 不存在，跳过。")
                continue

            self.progress.emit(f"正在为账号 '{account}' 执行上传任务...")
            uploader = Uploader(account_info['user_data_dir'])
            success_count, fail_count = 0, 0

            try:
                page = uploader.start_session()
                for i, video_path in enumerate(video_list):
                    if self.is_stopping:
                        self.progress.emit("上传任务已被用户取消")
                        break

                    base_name = os.path.splitext(os.path.basename(video_path))[0]
                    parts = base_name.split('#'); video_title = parts[0].strip()
                    filename_tags = [tag.strip() for tag in parts[1:] if tag.strip()]
                    final_tags = common_tags + filename_tags

                    success = uploader.upload_single_video(page, video_path, video_title, final_tags)
                    if success: success_count += 1
                    else: fail_count += 1

                    if i < len(video_list) - 1:
                        self.progress.emit(f"账号 '{account}': 暂停10秒，准备下一个视频...\n"); time.sleep(10)

                total_success += success_count
                total_fail += fail_count

                if success_count > 0 or fail_count > 0:
                    self.progress.emit(f"账号 '{account}' 完成！成功: {success_count}, 失败: {fail_count}")

            except Exception as e:
                self.progress.emit(f"账号 '{account}' 上传过程中发生错误: {e}")
                total_fail += len(video_list) - success_count
            finally:
                uploader.end_session()

            # 在不同账号间添加间隔
            if account != accounts[-1]:  # 不是最后一个账号
                self.progress.emit(f"\n切换到下一个账号，暂停15秒...\n")
                time.sleep(15)

        summary = f"多账号批量任务完成！总成功: {total_success}, 总失败: {total_fail}"
        self.finished.emit("success", summary)