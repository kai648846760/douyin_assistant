# dry_run_uploader.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang
# Simulates upload operations without Playwright side effects

import os
import time
import random
from typing import List, Optional, Callable
from rich.console import Console

console = Console()


class DryRunUploader:
    """
    Simulates video upload operations without actually using Playwright.
    Useful for testing, development, and when credentials are not available.
    """
    
    def __init__(self, user_data_dir: str = None, log_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the dry-run uploader
        
        Args:
            user_data_dir: User data directory (not used, kept for compatibility)
            log_callback: Optional callback function for logging
        """
        self.user_data_dir = user_data_dir
        self.log_callback = log_callback
        self.retry_count = 0
        self.max_retries = 3
        self.simulate_failures = False
        self.failure_rate = 0.1  # 10% failure rate for simulation
        
    def log(self, message: str, level: str = "info"):
        """Log a message"""
        prefix_map = {
            "info": "[cyan]",
            "success": "[green]",
            "warning": "[yellow]",
            "error": "[red]",
        }
        prefix = prefix_map.get(level, "[white]")
        suffix = "[/cyan]" if level == "info" else ""
        
        formatted_msg = f"{prefix}{message}{suffix}"
        
        if self.log_callback:
            self.log_callback(message)
        else:
            console.print(formatted_msg)
    
    def start_session(self):
        """
        Simulate starting a browser session
        
        Returns:
            A mock page object (self)
        """
        self.log("🔧 [DRY-RUN] 模拟启动浏览器会话...", "info")
        time.sleep(0.5)
        self.log("🔧 [DRY-RUN] 浏览器会话已启动（模拟）", "success")
        time.sleep(0.3)
        self.log("🔧 [DRY-RUN] 导航到上传页面（模拟）", "info")
        time.sleep(0.4)
        self.log("🔧 [DRY-RUN] 检查登录状态（模拟）", "info")
        time.sleep(0.3)
        self.log("✓ [DRY-RUN] 登录状态检查完成（模拟）", "success")
        return self
    
    def upload_single_video(self, page, video_path: str, title: str, tags: List[str] = None) -> bool:
        """
        Simulate uploading a single video
        
        Args:
            page: Mock page object (ignored)
            video_path: Path to the video file
            title: Video title
            tags: Optional list of tags
            
        Returns:
            True if simulation succeeds, False otherwise
        """
        video_name = os.path.basename(video_path)
        
        # Validate video file exists
        if not os.path.exists(video_path):
            self.log(f"✗ [DRY-RUN] 视频文件不存在: {video_path}", "error")
            return False
        
        # Get file size
        file_size = os.path.getsize(video_path)
        file_size_mb = file_size / (1024 * 1024)
        
        self.log(f"\n>>>>> [DRY-RUN] 开始处理: '{video_name}' <<<<<", "info")
        self.log(f"📁 视频大小: {file_size_mb:.2f} MB", "info")
        self.log(f"📝 标题: {title[:30]}", "info")
        
        if tags:
            self.log(f"🏷️  标签: {', '.join(tags)}", "info")
        
        # Simulate upload process
        self._simulate_upload_queue(video_name, file_size_mb)
        
        # Simulate potential failure
        if self.simulate_failures and random.random() < self.failure_rate:
            self.retry_count += 1
            if self.retry_count <= self.max_retries:
                self.log(f"⚠️  [DRY-RUN] 模拟上传失败，重试 {self.retry_count}/{self.max_retries}...", "warning")
                time.sleep(1)
                return self.upload_single_video(page, video_path, title, tags)
            else:
                self.log(f"✗ [DRY-RUN] 上传失败（已达到最大重试次数）", "error")
                self.retry_count = 0
                return False
        
        self.retry_count = 0
        self.log(f"✓ [DRY-RUN] 视频 '{video_name}' 上传成功！（模拟）", "success")
        return True
    
    def _simulate_upload_queue(self, video_name: str, file_size_mb: float):
        """Simulate the upload queue progression"""
        
        # Step 1: File selection
        self.log("  [>] 选择文件中...", "info")
        time.sleep(0.3)
        self.log("  [>] 文件已选择，等待跳转...", "info")
        time.sleep(0.4)
        
        # Step 2: Navigation to edit page
        self.log("  [>] 已进入编辑页面（模拟）", "info")
        time.sleep(0.3)
        
        # Step 3: Fill in metadata
        self.log("  [>] 填写标题和标签...", "info")
        time.sleep(0.5)
        self.log("  [>] 标题和标签已填写", "info")
        
        # Step 4: Video processing (simulated with progress)
        self.log("  [>] 视频处理中...", "info")
        processing_time = min(5, max(1, file_size_mb / 50))  # Simulate based on file size
        
        for i in range(int(processing_time * 2)):
            progress = (i + 1) / (processing_time * 2) * 100
            self.log(f"  [>] 处理进度: {progress:.0f}%", "info")
            time.sleep(0.5)
        
        self.log("  [>] 视频处理完成", "success")
        time.sleep(0.3)
        
        # Step 5: Publishing
        self.log("  [>] 发布中...", "info")
        time.sleep(0.8)
        self.log("  [✔] 发布成功！（模拟）", "success")
    
    def upload_video(self, video_path: str, title: str, tags: List[str] = None) -> bool:
        """
        Simulate uploading a video (self-contained mode)
        
        Args:
            video_path: Path to the video file
            title: Video title
            tags: Optional list of tags
            
        Returns:
            True if simulation succeeds, False otherwise
        """
        try:
            page = self.start_session()
            return self.upload_single_video(page, video_path, title, tags)
        finally:
            self.end_session()
    
    def end_session(self):
        """Simulate closing the browser session"""
        self.log("🔧 [DRY-RUN] 关闭浏览器会话（模拟）", "info")
        time.sleep(0.2)
        self.log("✓ [DRY-RUN] 浏览器会话已关闭", "success")
    
    def enable_failure_simulation(self, failure_rate: float = 0.1, max_retries: int = 3):
        """
        Enable failure simulation for testing retry logic
        
        Args:
            failure_rate: Probability of simulated failure (0.0 to 1.0)
            max_retries: Maximum number of retries before giving up
        """
        self.simulate_failures = True
        self.failure_rate = max(0.0, min(1.0, failure_rate))
        self.max_retries = max_retries
        self.log(f"⚠️  已启用失败模拟: 失败率 {self.failure_rate * 100:.0f}%, 最大重试 {self.max_retries} 次", "warning")
    
    def disable_failure_simulation(self):
        """Disable failure simulation"""
        self.simulate_failures = False
        self.log("✓ 已禁用失败模拟", "info")
