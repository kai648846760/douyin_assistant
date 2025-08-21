# downloader.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang

import os
import re
import requests
from typing import Dict, Optional

from config import HEADERS, DEFAULT_DOWNLOAD_PATH
from api_endpoints import USER_POST_API, USER_FAVORITE_API, USER_MIX_API

# 通用的请求参数，确保所有分页请求都能成功
BASE_API_PARAMS = {
    "device_platform": "webapp",
    "aid": "6383",
    "channel": "channel_pc_web",
}

class Downloader:
    """负责所有视频下载任务 (稳定版，仅包含主页/收藏/合集模式)"""

    def __init__(self, cookie: str, download_path: str = None):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.session.headers['Cookie'] = cookie
        self.download_path = download_path if download_path else DEFAULT_DOWNLOAD_PATH
        os.makedirs(self.download_path, exist_ok=True)
        print("下载器初始化完成。")

    def _fetch_data(self, url: str, params: Dict) -> Optional[Dict]:
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"请求API失败: {e}"); return None
        except requests.exceptions.JSONDecodeError:
            print("请求API失败: 服务器未返回有效的JSON数据，可能已被风控。"); return None

    def _download_single_video(self, aweme: Dict, sub_folder: str = ""):
        try:
            video_url = aweme['video']['play_addr']['url_list'][0]
            desc = aweme.get('desc', aweme['aweme_id'])
            valid_desc = "".join(c for c in desc if c not in r'\/:*?"<>|').strip()[:50]
            save_dir = os.path.join(self.download_path, sub_folder)
            os.makedirs(save_dir, exist_ok=True)
            filepath = os.path.join(save_dir, f"{valid_desc}.mp4")
            if os.path.exists(filepath):
                print(f"  [跳过] '{os.path.basename(filepath)}' 已存在."); return
            print(f"  [下载] 正在下载: '{os.path.basename(filepath)}'")
            video_response = requests.get(video_url, headers=HEADERS, stream=True, timeout=30)
            video_response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192): f.write(chunk)
        except (KeyError, IndexError, requests.RequestException) as e:
            print(f"  [失败] 下载视频 '{desc[:20]}...' 时发生错误: {e}")

    def _paginated_download(self, api_url: str, specific_params: dict, sub_folder: str, entity_name: str, name_key: str = None):
        """通用的分页下载逻辑"""
        cursor = 0; page = 1; folder_name = sub_folder
        base_params = BASE_API_PARAMS.copy()
        base_params.update(specific_params)

        while True:
            print(f"\n  正在获取第 {page} 页{entity_name}...")
            request_params = base_params.copy()
            request_params.update({"cursor": cursor, "count": 20})
            
            data = self._fetch_data(api_url, request_params)
            if not data or not data.get('aweme_list'): print(f"  未能获取到{entity_name}列表或已到达最后一页。"); break
            
            if page == 1 and name_key:
                info_dict = data.get(name_key, {})
                dynamic_name = info_dict.get('mix_name') or info_dict.get('name', sub_folder)
                folder_name = f"{sub_folder}_{''.join(c for c in dynamic_name if c not in r'\\/:*?\"<>|')}"
                print(f"  {entity_name}名称: {dynamic_name}")
            
            for aweme in data['aweme_list']: self._download_single_video(aweme, sub_folder=folder_name)
            if not data.get('has_more'): print(f"\n所有{entity_name}已处理完毕。"); break
            
            cursor = data.get('cursor'); page += 1

    def download_from_post(self, user_url: str):
        print(f"\n开始下载主页作品: {user_url}")
        match = re.search(r'user/(MS4wLjABAAAA[a-zA-Z0-9_-]+)', user_url)
        if not match: print("错误：无法从URL中解析出sec_user_id。"); return
        params = {"sec_user_id": match.group(1)}
        self._paginated_download(USER_POST_API, params, sub_folder=match.group(1), entity_name="主页作品")

    def download_from_favorite(self):
        print("\n开始下载我的收藏作品...")
        self._paginated_download(USER_FAVORITE_API, {}, sub_folder="MyFavorites", entity_name="收藏作品")
        
    def download_from_collection(self, collection_url: str):
        print(f"\n开始下载合集作品: {collection_url}")
        match = re.search(r'collection/(\d+)', collection_url)
        if not match: print("错误：无法从URL中解析出合集ID。"); return
        params = {"mix_id": match.group(1)}
        self._paginated_download(USER_MIX_API, params, sub_folder="Mix", entity_name="合集作品", name_key='mix_info')