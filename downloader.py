# -*- coding: utf-8 -*-
# @Author: Loki Wang

import os
import re
import requests
from typing import Dict, Optional
from urllib.parse import urlparse

from config import HEADERS, DEFAULT_DOWNLOAD_PATH
from api_endpoints import USER_POST_API, USER_FAVORITE_API

class Downloader:
    """负责所有视频下载任务"""

    def __init__(self, cookie: str):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.session.headers['Cookie'] = cookie
        os.makedirs(DEFAULT_DOWNLOAD_PATH, exist_ok=True)
        print("下载器初始化完成。")

    def _fetch_data(self, url: str, params: Dict) -> Optional[Dict]:
        """通用的API数据请求函数"""
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"请求API失败: {e}")
            return None

    def _download_single_video(self, aweme: Dict, sub_folder: str = ""):
        """下载单个无水印视频"""
        try:
            video_url = aweme['video']['play_addr']['url_list'][0]
            desc = aweme.get('desc', aweme['aweme_id'])
            valid_desc = "".join(c for c in desc if c not in r'\/:*?"<>|').strip()[:50]
            save_dir = os.path.join(DEFAULT_DOWNLOAD_PATH, sub_folder)
            os.makedirs(save_dir, exist_ok=True)
            filepath = os.path.join(save_dir, f"{valid_desc}.mp4")
            if os.path.exists(filepath):
                print(f"  [跳过] '{os.path.basename(filepath)}' 已存在.")
                return
            print(f"  [下载] 正在下载: '{os.path.basename(filepath)}'")
            video_response = requests.get(video_url, headers=HEADERS, stream=True, timeout=30)
            video_response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except (KeyError, IndexError, requests.RequestException) as e:
            print(f"  [失败] 下载视频 '{desc[:20]}...' 时发生错误: {e}")

    def download_from_user_post(self, user_url: str):
        """下载指定用户主页发布的所有视频"""
        print(f"\n开始下载用户主页视频: {user_url}")
        
        match = re.search(r'user/(MS4wLjABAAAA[a-zA-Z0-9_-]+)', user_url)
        if not match:
             print("错误：无法从提供的URL中解析出有效的sec_user_id。请确保URL格式正确。")
             return
        
        sec_user_id = match.group(1)
        print(f"成功解析到 sec_user_id: {sec_user_id}")

        max_cursor = 0
        page = 1
        while True:
            print(f"\n正在获取第 {page} 页视频...")
            params = {
                "device_platform": "webapp", "aid": "6383", "channel": "channel_pc_web",
                "sec_user_id": sec_user_id, "max_cursor": max_cursor, "count": 20
            }
            data = self._fetch_data(USER_POST_API, params)

            if not data or not data.get('aweme_list'):
                print("未能获取到视频列表或已到达最后一页。")
                break
            
            aweme_list = data['aweme_list']
            for aweme in aweme_list:
                self._download_single_video(aweme, sub_folder=sec_user_id)
            
            if not data.get('has_more'):
                print("\n所有视频页已处理完毕。")
                break
            
            max_cursor = data['max_cursor']
            page += 1

    def download_from_favorites(self):
        """下载当前登录账号收藏的所有视频"""
        print("\n开始下载收藏夹视频...")
        max_cursor = 0
        page = 1
        while True:
            print(f"\n正在获取第 {page} 页收藏...")
            params = {
                "device_platform": "webapp", "aid": "6383", "channel": "channel_pc_web",
                "max_cursor": max_cursor, "count": 20
            }
            data = self._fetch_data(USER_FAVORITE_API, params)

            if not data or not data.get('aweme_list'):
                print("未能获取到收藏列表或已到达最后一页。")
                break

            aweme_list = data['aweme_list']
            for aweme in aweme_list:
                self._download_single_video(aweme, sub_folder="favorites")

            if not data.get('has_more'):
                print("\n所有收藏页已处理完毕。")
                break

            max_cursor = data['max_cursor']
            page += 1