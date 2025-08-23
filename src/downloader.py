# downloader.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang

import os
import re
import requests
from typing import Dict, Optional

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import HEADERS, DEFAULT_DOWNLOAD_PATH
from .api_endpoints import (
    SINGLE_VIDEO_API, USER_POST_API, USER_LIKE_API, USER_FAVORITE_API,
    USER_COLLECTS_API, USER_MIX_API, MUSIC_API, LIVE_API
)
from .xbogus import ABogusManager

# 通用的请求参数，确保所有分页请求都能成功
BASE_API_PARAMS = {
    "device_platform": "webapp",
    "aid": "6383",
    "channel": "channel_pc_web",
}

class AwemeIdFetcher:
    """从抖音URL中提取aweme_id的简单实现"""

    @staticmethod
    def get_aweme_id(url: str) -> str:
        """从URL中提取aweme_id"""
        # 抖音视频URL模式
        patterns = [
            r"video/([^/?]*)",  # https://www.douyin.com/video/7458200834908622137
            r"v.douyin.com/([^/?]*)",  # https://v.douyin.com/i2wyU53P/
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        raise ValueError(f"无法从URL中提取aweme_id: {url}")

class Downloader:
    """负责所有视频下载任务"""

    def __init__(self, cookie: str, download_path: str = None):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.session.headers['Cookie'] = cookie
        self.download_path = download_path if download_path else DEFAULT_DOWNLOAD_PATH
        os.makedirs(self.download_path, exist_ok=True)
        self._stop_requested = False  # 停止标志
        print("下载器初始化完成。")

    def _fetch_data(self, url: str, params: Dict) -> Optional[Dict]:
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.JSONDecodeError:
            print("请求API失败: 服务器未返回有效的JSON数据，可能已被风控。")
            return None
        except requests.RequestException as e:
            print(f"请求API失败: {e}")
            return None

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
            # 检查是否需要停止下载
            if hasattr(self, '_stop_requested') and self._stop_requested:
                print(f"\n  [停止] 用户请求停止{entity_name}下载")
                break

            print(f"\n  正在获取第 {page} 页{entity_name}...")
            request_params = base_params.copy()
            request_params.update({"cursor": cursor, "count": 20})

            data = self._fetch_data(api_url, request_params)
            if not data or not data.get('aweme_list'): print(f"  未能获取到{entity_name}列表或已到达最后一页。"); break

            if page == 1 and name_key:
                info_dict = data.get(name_key, {})
                dynamic_name = info_dict.get('mix_name') or info_dict.get('name', sub_folder)
                invalid_chars = r'\/:*?"<>|'
                folder_name = f"{sub_folder}_{''.join(c for c in dynamic_name if c not in invalid_chars)}"
                print(f"  {entity_name}名称: {dynamic_name}")

            for aweme in data['aweme_list']:
                # 检查是否需要停止下载
                if hasattr(self, '_stop_requested') and self._stop_requested:
                    print(f"\n  [停止] 用户请求停止{entity_name}下载")
                    return
                self._download_single_video(aweme, sub_folder=folder_name)

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

    def download_from_like(self):
        """下载用户点赞的作品"""
        print("\n开始下载我的点赞作品...")
        self._paginated_download(USER_LIKE_API, {}, sub_folder="MyLikes", entity_name="点赞作品")

    def download_from_collects(self, collects_url: str):
        """下载收藏夹作品 (对应F2的collects功能)"""
        print(f"\n开始下载收藏夹作品: {collects_url}")
        match = re.search(r'collects/(\d+)', collects_url)
        if not match: print("错误：无法从URL中解析出收藏夹ID。"); return
        params = {"collects_id": match.group(1)}
        self._paginated_download(USER_COLLECTS_API, params, sub_folder="MyCollects", entity_name="收藏夹作品")

    def download_from_music(self, music_url: str):
        """下载指定音乐的所有作品"""
        print(f"\n开始下载音乐作品: {music_url}")
        match = re.search(r'music/(\d+)', music_url)
        if not match: print("错误：无法从URL中解析出音乐ID。"); return
        params = {"music_id": match.group(1)}
        self._paginated_download(MUSIC_API, params, sub_folder="Music", entity_name="音乐作品")

    def download_from_url(self, video_url: str):
        """下载单个视频作品 - 参考F2项目实现"""
        print(f"\n开始下载单个视频: {video_url}")

        try:
            # 使用AwemeIdFetcher从URL中提取aweme_id
            aweme_id = AwemeIdFetcher.get_aweme_id(video_url)
            print(f"提取到的aweme_id: {aweme_id}")
        except ValueError as e:
            print(f"错误：{e}")
            return

        # 使用F2项目风格的参数传递方式
        params = {"aweme_id": aweme_id}

        # 构建完整的参数（包含基础参数）
        full_params = BASE_API_PARAMS.copy()
        full_params.update(params)

        # 添加ABogus参数（如果可用）
        try:
            user_agent = self.session.headers.get("User-Agent", "")
            param_str = "&".join([f"{k}={v}" for k, v in params.items()])
            enhanced_url = ABogusManager.str_2_endpoint(user_agent, param_str)

            print(f"ABogus增强URL: {enhanced_url}")

            # 解析ABogusManager返回的URL参数
            if '?' in enhanced_url:
                query_part = enhanced_url.split('?', 1)[1]
                print(f"ABogus查询参数: {query_part}")

                # 解析所有参数
                for pair in query_part.split('&'):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        if key == 'a_bogus':
                            full_params['a_bogus'] = value
                            print(f"已添加ABogus参数: {value}")
                        elif key not in full_params:  # 避免覆盖已有参数
                            full_params[key] = value

            # 确保有a_bogus参数
            if 'a_bogus' not in full_params:
                print("未找到a_bogus参数，使用默认值")
                full_params['a_bogus'] = '0'

        except Exception as e:
            print(f"ABogus参数处理失败，使用基础参数: {e}")
            # 即使ABogus失败，也要确保有a_bogus参数
            full_params['a_bogus'] = '0'  # 使用默认值

        data = self._fetch_data(SINGLE_VIDEO_API, full_params)
        if not data:
            print("错误：API请求失败，返回None")
            return

        if not data.get('aweme_detail'):
            print("错误：无法获取视频详情信息。")
            print(f"API响应: {data}")
            return

        aweme = data['aweme_detail']
        print(f"成功获取视频信息: {aweme.get('desc', '无描述')[:50]}...")
        self._download_single_video(aweme, sub_folder="SingleVideos")

    def download_live(self, live_url: str):
        """直播下载功能 (基础实现，F2有更完整的直播功能)"""
        print(f"\n直播下载功能: {live_url}")
        print("⚠️  直播下载功能尚未完全实现，这是一个占位方法。")
        print("    F2项目提供了完整的直播RTMP流下载和弹幕采集功能。")
        print("    如需完整功能，请参考F2项目的直播下载实现。")

    # 别名方法，确保与worker.py的调用兼容
    def download_from_mix(self, mix_url: str):
        """别名方法，与download_from_collection功能相同"""
        return self.download_from_collection(mix_url)