# main.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang

import os
import time
import argparse
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from .account_manager import AccountManager
from .downloader import Downloader
from .uploader import Uploader

console = Console()
account_manager = AccountManager()
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.webm', '.avi')

def print_welcome_message():
    rprint(Panel("[bold cyan]抖音全能助手[/bold cyan]\n[bold white]一个由 Loki Wang 开发的，支持多账号的抖音视频工具。[/bold white]", title="✨ 欢迎使用 ✨", title_align="center", border_style="purple"))

def main():
    print_welcome_message()
    parser = argparse.ArgumentParser(description="抖音全能助手 - 自动管理账号，轻松爬取与发布。")
    subparsers = parser.add_subparsers(dest="command", help="选择一个命令", required=True)

    # --- 账号管理命令 ---
    parser_list = subparsers.add_parser("list", help="列出所有已配置的抖音账号及其状态。")
    parser_list.set_defaults(func=lambda args: account_manager.list_accounts())
    parser_add = subparsers.add_parser("add-account", help="添加一个新的账号配置。")
    parser_add.add_argument("-u", "--username", required=True, help="要添加的新账号的唯一用户名。")
    parser_add.add_argument("--remark", default="", help="为账号添加备注 (可选)。")
    parser_add.set_defaults(func=lambda args: account_manager.add_account(args.username, args.remark))
    parser_cookie = subparsers.add_parser("cookie", help="从本地浏览器自动获取并更新指定账号的Cookie。")
    parser_cookie.add_argument("-a", "--account", required=True, help="要更新Cookie的账号用户名。")
    parser_cookie.add_argument("-b", "--browser", default="chrome", choices=['chrome', 'firefox', 'edge', 'opera', 'brave', 'chromium'], help="指定从哪个浏览器获取Cookie (默认: chrome)。")
    parser_cookie.set_defaults(func=lambda args: account_manager.update_cookie_from_browser(args.account, args.browser))

    # --- 功能命令 (回滚到稳定版) ---
    parser_download = subparsers.add_parser("download", help="下载抖音视频。")
    parser_download.add_argument("-a", "--account", required=True, help="用于下载的抖音账号用户名。")
    parser_download.add_argument("-m", "--mode", required=True, 
                                 choices=['post', 'favorite', 'collection'], 
                                 help="下载模式: post(主页), favorite(收藏), collection(合集)。")
    parser_download.add_argument("-u", "--url", help="当模式为 post 或 collection 时，指定目标URL。")
    parser_download.set_defaults(func=download_command)

    parser_upload = subparsers.add_parser("upload", help="上传单个视频到抖音。")
    parser_upload.add_argument("-a", "--account", required=True, help="用于上传的抖音账号用户名。")
    parser_upload.add_argument("-p", "--video_path", required=True, help="本地视频文件的完整路径。")
    parser_upload.add_argument("-t", "--title", required=True, help="视频的标题或描述。")
    parser_upload.add_argument("--tags", default="", help="视频标签，多个标签用逗号分隔。")
    parser_upload.set_defaults(func=upload_command)
    
    parser_batch_upload = subparsers.add_parser("batch-upload", help="批量上传指定目录下的所有视频。")
    parser_batch_upload.add_argument("-a", "--account", required=True, help="用于上传的抖音账号用户名。")
    parser_batch_upload.add_argument("-d", "--dir_path", required=True, help="包含视频文件的目录路径。")
    parser_batch_upload.add_argument("--tags", default="", help="为所有视频添加的通用标签。")
    parser_batch_upload.set_defaults(func=batch_upload_command)

    args = parser.parse_args()
    args.func(args)

# ----------------- 命令执行函数 -----------------
def download_command(args):
    account_info = account_manager.get_account(args.account)
    if not account_info or not account_info.get('cookie'):
        console.print(f"[bold red]下载失败: 账号 '{args.account}' 不存在或尚未配置Cookie。[/bold red]"); return

    downloader = Downloader(account_info['cookie'])
    
    if args.mode in ['post', 'collection'] and not args.url:
        console.print(f"[bold red]错误: '{args.mode}' 模式需要提供 --url 参数。[/bold red]"); return
    
    if args.mode == 'post': downloader.download_from_post(args.url)
    elif args.mode == 'favorite': downloader.download_from_favorite()
    elif args.mode == 'collection': downloader.download_from_collection(args.url)

def common_upload_logic(account_name, func):
    account_info = account_manager.get_account(account_name)
    if not account_info: console.print(f"[bold red]上传失败: 指定账号 '{account_name}' 不存在。[/bold red]"); return
    user_data_dir = account_info.get('user_data_dir')
    if not user_data_dir: console.print(f"[bold red]错误: 账号 '{account_name}' 未配置 'user_data_dir'。[/bold red]"); return
    
    uploader = Uploader(user_data_dir)
    try:
        page = uploader.start_session()
        func(uploader, page)
    finally:
        uploader.end_session()

def upload_command(args):
    def do_upload(uploader, page):
        tags = [t.strip() for t in args.tags.split(',') if t.strip()] if args.tags else []
        success = uploader.upload_single_video(page, args.video_path, args.title, tags)
        if success: console.print("[bold green]\n单视频发布任务已成功完成。[/bold green]")
        else: console.print("[bold red]\n单视频发布任务失败。[/bold red]")
    common_upload_logic(args.account, do_upload)

def batch_upload_command(args):
    if not os.path.isdir(args.dir_path): console.print(f"[bold red]错误: 路径 '{args.dir_path}' 不是有效目录。[/bold red]"); return
    video_files = [f for f in os.listdir(args.dir_path) if f.lower().endswith(VIDEO_EXTENSIONS)]
    if not video_files: console.print(f"[bold yellow]目录 '{args.dir_path}' 中无视频文件。[/bold yellow]"); return
    
    console.print(f"[bold cyan]发现 {len(video_files)} 个视频待上传。即将开始批量任务...[/bold cyan]")
    
    def do_batch_upload(uploader, page):
        common_tags = [t.strip() for t in args.tags.split(',') if t.strip()] if args.tags else []
        success_count, fail_count = 0, 0
        for i, filename in enumerate(video_files):
            video_path = os.path.join(args.dir_path, filename)
            base_name = os.path.splitext(filename)[0]
            parts = base_name.split('#'); video_title = parts[0].strip()
            filename_tags = [tag.strip() for tag in parts[1:] if tag.strip()]
            final_tags = common_tags + filename_tags
            success = uploader.upload_single_video(page, video_path, video_title, final_tags)
            if success: success_count += 1
            else: fail_count += 1
            if i < len(video_files) - 1:
                console.print("[yellow]暂停10秒，准备下一个任务...[/yellow]"); time.sleep(10)
        console.print(Panel(f"[bold]批量上传任务完成！\n成功: {success_count} 个\n失败: {fail_count} 个[/bold]", border_style="green"))
    common_upload_logic(args.account, do_batch_upload)

if __name__ == "__main__":
    main()