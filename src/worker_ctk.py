# worker_ctk.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang
# CustomTkinter版本的后台工作线程，完整保留所有原始功能

import os
import sys
import subprocess
import threading
import time
from typing import List, Dict, Optional, Callable
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.account_manager import AccountManager
    from src.uploader import Uploader
    from src.downloader import Downloader
except ImportError as e:
    print(f"导入错误: {e}")
    # 如果导入失败，创建占位符类
    class AccountManager:
        def __init__(self):
            pass
    
    class Uploader:
        def __init__(self, *args, **kwargs):
            pass
    
    class Downloader:
        def __init__(self, *args, **kwargs):
            pass

class WorkerCTK:
    """CustomTkinter版本的后台工作线程，完整保留所有原始功能"""
    
    def __init__(self):
        self.account_manager = AccountManager()
        self.uploader = None  # 将在需要时创建
        self.downloader = None  # 将在需要时创建
        
        # 回调函数
        self.progress_callback: Optional[Callable[[str], None]] = None
        self.finished_callback: Optional[Callable[[str, str], None]] = None
        
        # 任务控制
        self.is_stopping = False
        self.current_process: Optional[subprocess.Popen] = None
        self.current_thread: Optional[threading.Thread] = None
        
        # 日志缓冲
        self._log_buffer = []
        self._log_lock = threading.Lock()
    
    def log(self, message: str):
        """记录日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}\n"
        
        with self._log_lock:
            self._log_buffer.append(formatted_msg)
        
        if self.progress_callback:
            self.progress_callback(formatted_msg)
    
    def set_task_running(self, is_running: bool):
        """设置任务运行状态"""
        self.is_stopping = not is_running
    
    def stop_download(self):
        """停止当前下载任务"""
        self.is_stopping = True
        
        # 设置downloader的停止标志
        if self.downloader:
            self.downloader._stop_requested = True
            self.log("已发送停止信号给下载器")
        
        if self.current_process:
            try:
                self.log("正在终止下载进程...")
                self.current_process.terminate()
                
                # 等待进程结束，最多等待5秒
                try:
                    self.current_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.log("进程未响应，强制终止...")
                    self.current_process.kill()
                    self.current_process.wait()
                
                self.log("下载任务已停止")
            except Exception as e:
                self.log(f"停止下载时发生错误: {e}")
            finally:
                self.current_process = None
        else:
            self.log("正在停止下载任务...")
        
        if callable(self.finished_callback):
            self.finished_callback("info", "下载任务已停止")
    
    def run_update_cookie(self, account_name: str, browser: str):
        """运行更新Cookie任务"""
        try:
            self.is_stopping = False
            self.log(f"开始为账号 '{account_name}' 从 {browser} 浏览器更新Cookie...")
            
            # 获取账号信息
            account_info = self.account_manager.get_account(account_name)
            if not account_info:
                raise Exception(f"账号 '{account_name}' 不存在")
            
            # 调用账号管理器的更新Cookie方法
            success = self.account_manager.update_cookie_from_browser(account_name, browser)
            
            if success:
                self.log(f"账号 '{account_name}' 的Cookie更新成功")
                if callable(self.finished_callback):
                    self.finished_callback("success", f"账号 '{account_name}' 的Cookie更新成功")
            else:
                raise Exception(f"无法从 {browser} 浏览器获取Cookie")
                
        except Exception as e:
            error_msg = f"更新Cookie失败: {str(e)}"
            self.log(error_msg)
            if callable(self.finished_callback):
                self.finished_callback("error", error_msg)
    
    def run_download(self, account_name: str, mode: str, url: str, custom_path: str = ""):
        """运行下载任务"""
        try:
            self.is_stopping = False
            self.log(f"开始下载任务 - 账号: {account_name}, 模式: {mode}")
            
            # 获取账号信息
            account_info = self.account_manager.get_account(account_name)
            if not account_info:
                raise Exception(f"账号 '{account_name}' 不存在")
            
            if not account_info.get('cookie'):
                raise Exception(f"账号 '{account_name}' 没有配置Cookie，请先更新Cookie")
            
            # 构建下载参数
            download_args = {
                'account_name': account_name,
                'mode': mode,
                'url': url,
                'custom_path': custom_path
            }
            
            # 根据不同模式调用相应的下载方法
            if mode == 'post':
                self._download_user_posts(download_args)
            elif mode == 'like':
                self._download_user_likes(download_args)
            elif mode == 'collection':
                self._download_user_collections(download_args)
            elif mode == 'collects':
                self._download_collects(download_args)
            elif mode == 'mix':
                self._download_mix(download_args)
            elif mode == 'music':
                self._download_music(download_args)
            elif mode == 'live':
                self._download_live(download_args)
            elif mode == 'one':
                self._download_single_video(download_args)
            else:
                raise Exception(f"不支持的下载模式: {mode}")
            
            if not self.is_stopping:
                self.log("下载任务完成")
                if callable(self.finished_callback):
                    self.finished_callback("success", "下载任务完成")
                    
        except Exception as e:
            error_msg = f"下载失败: {str(e)}"
            self.log(error_msg)
            if callable(self.finished_callback):
                self.finished_callback("error", error_msg)
    
    def _download_user_posts(self, args: Dict):
        """下载用户主页作品"""
        self.log("开始下载用户主页作品...")
        self._execute_download_command(args, "post")
    
    def _download_user_likes(self, args: Dict):
        """下载用户点赞作品"""
        self.log("开始下载用户点赞作品...")
        self._execute_download_command(args, "like")
    
    def _download_user_collections(self, args: Dict):
        """下载用户收藏作品"""
        self.log("开始下载用户收藏作品...")
        self._execute_download_command(args, "collection")
    
    def _download_collects(self, args: Dict):
        """下载收藏夹作品"""
        self.log("开始下载收藏夹作品...")
        self._execute_download_command(args, "collects")
    
    def _download_mix(self, args: Dict):
        """下载合集作品"""
        self.log("开始下载合集作品...")
        self._execute_download_command(args, "mix")
    
    def _download_music(self, args: Dict):
        """下载音乐作品"""
        self.log("开始下载音乐作品...")
        self._execute_download_command(args, "music")
    
    def _download_live(self, args: Dict):
        """下载直播"""
        self.log("开始下载直播...")
        self._execute_download_command(args, "live")
    
    def _download_single_video(self, args: Dict):
        """下载单个视频"""
        self.log("开始下载单个视频...")
        self._execute_download_command(args, "one")
    
    def _execute_download_command(self, args: Dict, mode: str):
        """执行下载命令"""
        try:
            # 获取账号Cookie
            account_info = self.account_manager.get_account(args['account_name'])
            cookie = account_info.get('cookie')
            
            # 动态创建downloader实例并保存为类属性
            self.downloader = Downloader(cookie, args.get('custom_path', ''))
            
            # 根据模式调用相应的下载方法
            if mode == 'post':
                self.downloader.download_from_post(args['url'])
                result = True
            elif mode == 'like':
                self.downloader.download_from_like()
                result = True
            elif mode == 'collection':
                self.downloader.download_from_collection(args['url'])
                result = True
            elif mode == 'collects':
                self.downloader.download_from_collects(args['url'])
                result = True
            elif mode == 'mix':
                self.downloader.download_from_mix(args['url'])
                result = True
            elif mode == 'music':
                self.downloader.download_from_music(args['url'])
                result = True
            elif mode == 'live':
                self.downloader.download_live(args['url'])
                result = True
            elif mode == 'one':
                self.downloader.download_from_url(args['url'])
                result = True
            else:
                result = False
            
            if not result:
                raise Exception("下载失败")
                
        except Exception as e:
            raise Exception(f"执行下载命令时发生错误: {str(e)}")
    
    def run_single_upload(self, account_name: str, video_path: str, tags: List[str] = None):
        """运行单个视频上传任务"""
        try:
            self.is_stopping = False
            self.log(f"开始上传视频 '{os.path.basename(video_path)}' 到账号 '{account_name}'...")
            
            # 获取账号信息
            account_info = self.account_manager.get_account(account_name)
            if not account_info:
                raise Exception(f"账号 '{account_name}' 不存在")
            
            user_data_dir = account_info.get('user_data_dir')
            if not user_data_dir or not os.path.isdir(user_data_dir):
                raise Exception(f"账号 '{account_name}' 没有配置有效的用户数据目录")
            
            # 动态创建uploader实例
            uploader = Uploader(user_data_dir)
            
            # 解析视频标题和标签
            video_name = os.path.basename(video_path)
            title = os.path.splitext(video_name)[0]
            
            # 使用uploader模块执行上传
            result = uploader.upload_video(video_path, title, tags or [])
            
            if result:
                self.log(f"视频 '{os.path.basename(video_path)}' 上传成功")
                if callable(self.finished_callback):
                    self.finished_callback("success", f"视频上传成功: {os.path.basename(video_path)}")
            else:
                raise Exception("上传失败")
                
        except Exception as e:
            error_msg = f"上传失败: {str(e)}"
            self.log(error_msg)
            if callable(self.finished_callback):
                self.finished_callback("error", error_msg)
    
    def run_batch_upload(self, account_names: List[str], video_paths: List[str], common_tags: List[str] = None):
        """运行批量上传任务"""
        try:
            self.is_stopping = False
            total_videos = len(video_paths)
            total_accounts = len(account_names)
            total_tasks = total_videos * total_accounts
            
            self.log(f"开始批量上传任务: {total_videos} 个视频 × {total_accounts} 个账号 = {total_tasks} 个任务")
            
            # 验证所有账号
            valid_accounts = []
            for account_name in account_names:
                account_info = self.account_manager.get_account(account_name)
                if not account_info:
                    self.log(f"警告: 账号 '{account_name}' 不存在，跳过")
                    continue
                
                user_data_dir = account_info.get('user_data_dir')
                if not user_data_dir or not os.path.isdir(user_data_dir):
                    self.log(f"警告: 账号 '{account_name}' 没有配置有效的用户数据目录，跳过")
                    continue
                
                valid_accounts.append(account_name)
            
            if not valid_accounts:
                raise Exception("没有有效的上传账号")
            
            self.log(f"有效账号: {', '.join(valid_accounts)}")
            
            # 执行批量上传
            success_count = 0
            failed_count = 0
            
            for i, video_path in enumerate(video_paths, 1):
                if self.is_stopping:
                    self.log("用户取消了批量上传任务")
                    break
                
                video_name = os.path.basename(video_path)
                self.log(f"\n处理视频 {i}/{total_videos}: {video_name}")
                
                # 解析视频文件名中的标签
                video_tags = self._parse_video_tags(video_name)
                all_tags = (common_tags or []) + video_tags
                
                for j, account_name in enumerate(valid_accounts, 1):
                    if self.is_stopping:
                        break
                    
                    self.log(f"  上传到账号 {j}/{len(valid_accounts)}: {account_name}")
                    
                    try:
                        # 动态创建uploader实例
                        account_info = self.account_manager.get_account(account_name)
                        user_data_dir = account_info.get('user_data_dir')
                        uploader = Uploader(user_data_dir)
                        
                        # 解析视频标题
                        video_name = os.path.basename(video_path)
                        title = os.path.splitext(video_name)[0]
                        
                        # 使用uploader模块执行上传
                        result = uploader.upload_video(video_path, title, all_tags)
                        
                        if result:
                            success_count += 1
                            self.log(f"  ✓ 成功上传到 {account_name}")
                        else:
                            failed_count += 1
                            self.log(f"  ✗ 上传到 {account_name} 失败")
                    
                    except Exception as e:
                        failed_count += 1
                        self.log(f"  ✗ 上传到 {account_name} 时发生错误: {str(e)}")
                    
                    # 添加延迟避免过于频繁的操作
                    if not self.is_stopping and j < len(valid_accounts):
                        time.sleep(2)
                
                # 视频间的延迟
                if not self.is_stopping and i < total_videos:
                    time.sleep(3)
            
            # 任务完成总结
            if not self.is_stopping:
                summary = f"批量上传完成: 成功 {success_count} 个，失败 {failed_count} 个"
                self.log(f"\n{summary}")
                
                if callable(self.finished_callback):
                    if failed_count == 0:
                        self.finished_callback("success", summary)
                    else:
                        self.finished_callback("info", summary)
            
        except Exception as e:
            error_msg = f"批量上传失败: {str(e)}"
            self.log(error_msg)
            if callable(self.finished_callback):
                self.finished_callback("error", error_msg)
    
    def _parse_video_tags(self, filename: str) -> List[str]:
        """从视频文件名中解析标签"""
        tags = []
        try:
            # 移除文件扩展名
            name_without_ext = os.path.splitext(filename)[0]
            
            # 查找所有以#开头的标签
            import re
            tag_matches = re.findall(r'#([^#\s]+)', name_without_ext)
            tags.extend(tag_matches)
            
        except Exception as e:
            self.log(f"解析视频标签时发生错误: {e}")
        
        return tags
    
    def get_log_buffer(self) -> List[str]:
        """获取日志缓冲区内容"""
        with self._log_lock:
            return self._log_buffer.copy()
    
    def clear_log_buffer(self):
        """清空日志缓冲区"""
        with self._log_lock:
            self._log_buffer.clear()


if __name__ == "__main__":
    # 测试代码
    worker = WorkerCTK()
    worker.progress_callback = print
    worker.log("WorkerCTK 初始化完成")