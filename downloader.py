# -*- coding: utf-8 -*-
# @Author: Loki Wang

import os
import re
import requests
from typing import Dict, Optional
from urllib.parse import urlparse

from rich.console import Console
from config import HEADERS, DEFAULT_DOWNLOAD_PATH
from api_endpoints import USER_POST_API, USER_FAVORITE_API, USER_COLLECTION_API

console = Console()

class Downloader:
    """负责所有视频下载任务"""

    def __init__(self, cookie: str):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.session.headers['Cookie'] = cookie
        os.makedirs(DEFAULT_DOWNLOAD_PATH, exist_ok=True)
        console.print("[bold green]下载器初始化完成。[/bold green]")

    def _fetch_data(self, url: str, params: Dict) -> Optional[Dict]:
        """通用的API数据请求函数"""
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            console.print(f"[bold red]请求API失败: {e}[/bold red]")
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
                console.print(f"  [yellow]跳过[/yellow] '{os.path.basename(filepath)}' 已存在.")
                return

            console.print(f"  [green]下载[/green] 正在下载: '{os.path.basename(filepath)}'")
            video_response = requests.get(video_url, headers=HEADERS, stream=True, timeout=30)
            video_response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    f.write(chunk)

        except (KeyError, IndexError, requests.RequestException) as e:
            console.print(f"  [red]失败[/red] 下载视频 '{desc[:20]}...' 时发生错误: {e}")

    def download_from_user_post(self, user_url: str):
        """下载指定用户主页发布的所有视频"""
        console.print(f"\n[cyan]开始下载用户主页视频:[/cyan] {user_url}")
        
        match = re.search(r'user/(MS4wLjABAAAA[a-zA-Z0-9_-]+)', user_url)
        if not match:
             console.print("[bold red]错误：无法从提供的URL中解析出有效的sec_user_id。[/bold red]")
             return
        
        sec_user_id = match.group(1)
        console.print(f"  [blue]解析到 sec_user_id:[/blue] {sec_user_id}")

        max_cursor = 0
        page = 1
        while True:
            console.print(f"\n  [bold]正在获取第 {page} 页视频...[/bold]")
            params = { "sec_user_id": sec_user_id, "max_cursor": max_cursor, "count": 20 }
            data = self._fetch_data(USER_POST_API, params)

            if not data or not data.get('aweme_list'):
                console.print("  [yellow]未能获取到视频列表或已到达最后一页。[/yellow]")
                break
            
            aweme_list = data['aweme_list']
            for aweme in aweme_list:
                self._download_single_video(aweme, sub_folder=sec_user_id)
            
            if not data.get('has_more'):
                console.print("\n[bold green]所有视频页已处理完毕。[/bold green]")
                break
            
            max_cursor = data['max_cursor']
            page += 1

    def download_from_favorites(self):
        """下载当前登录账号收藏的所有视频"""
        console.print("\n[cyan]开始下载收藏夹视频...[/cyan]")
        max_cursor = 0
        page = 1
        while True:
            console.print(f"\n  [bold]正在获取第 {page} 页收藏...[/bold]")
            params = { "max_cursor": max_cursor, "count": 20 }
            data = self._fetch_data(USER_FAVORITE_API, params)

            if not data or not data.get('aweme_list'):
                console.print("  [yellow]未能获取到收藏列表或已到达最后一页。[/yellow]")
                break

            aweme_list = data['aweme_list']
            for aweme in aweme_list:
                self._download_single_video(aweme, sub_folder="MyFavorites")

            if not data.get('has_more'):
                console.print("\n[bold green]所有收藏页已处理完毕。[/bold green]")
                break

            max_cursor = data['max_cursor']
            page += 1

    def download_from_collection(self, collection_url: str):
        """【已修正】下载指定合集的所有视频"""
        console.print(f"\n[cyan]开始下载合集视频:[/cyan] {collection_url}")
        
        match = re.search(r'collection/(\d+)', collection_url)
        if not match:
             console.print("[bold red]错误：无法从提供的URL中解析出有效的合集ID。[/bold red]")
             return
        
        collection_id = match.group(1)
        console.print(f"  [blue]解析到 合集ID:[/blue] {collection_id}")

        cursor = 0
        page = 1
        sub_folder_name = None

        while True:
            console.print(f"\n  [bold]正在获取第 {page} 页视频...[/bold]")
            # 【修正】使用正确的参数名 mix_id
            params = { "mix_id": collection_id, "cursor": cursor, "count": 30 }
            data = self._fetch_data(USER_COLLECTION_API, params)

            if not data or not data.get('aweme_list'):
                console.print("  [yellow]未能获取到视频列表或已到达最后一页。[/yellow]")
                break
            
            if sub_folder_name is None:
                # 【修正】使用正确的字段名 mix_info 和 mix_name
                collection_name = data.get('mix_info', {}).get('mix_name', collection_id)
                sub_folder_name = f"collection_{''.join(c for c in collection_name if c not in r'\\/:*?\"<>|')}"
                console.print(f"  [blue]合集名称:[/blue] {collection_name}")

            aweme_list = data['aweme_list']
            for aweme in aweme_list:
                self._download_single_video(aweme, sub_folder=sub_folder_name)
            
            if not data.get('has_more'):
                console.print("\n[bold green]所有合集视频已处理完毕。[/bold green]")
                break
            
            cursor = data.get('cursor')
            page += 1