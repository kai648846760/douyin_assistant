# -*- coding: utf-8 -*-
# @Author: Loki Wang

import argparse
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from account_manager import AccountManager
from downloader import Downloader
from uploader import Uploader

# 初始化 rich console 和账号管理器
console = Console()
account_manager = AccountManager()

def print_welcome_message():
    """打印欢迎信息"""
    rprint(
        Panel(
            "[bold cyan]抖音全能助手[/bold cyan]\n"
            "[bold white]一个由 Loki Wang 开发的，支持多账号的抖音视频工具。[/bold white]",
            title="✨ 欢迎使用 ✨",
            title_align="center",
            border_style="purple"
        )
    )

def main():
    print_welcome_message()

    parser = argparse.ArgumentParser(description="抖音全能助手 - 自动管理账号，轻松爬取与发布。")
    subparsers = parser.add_subparsers(dest="command", help="选择一个命令", required=True)

    # --- 账号管理命令 ---
    parser_list = subparsers.add_parser("list", help="列出所有已配置的抖音账号及其状态。")
    parser_list.set_defaults(func=lambda args: account_manager.list_accounts())

    parser_add = subparsers.add_parser("add-account", help="添加一个新的账号配置。")
    parser_add.add_argument("-u", "--username", required=True, help="要添加的新账号的唯一用户名（例如 '我的大号'）。")
    parser_add.set_defaults(func=lambda args: account_manager.add_account(args.username))

    parser_cookie = subparsers.add_parser("cookie", help="从本地浏览器自动获取并更新指定账号的Cookie。")
    parser_cookie.add_argument("-a", "--account", required=True, help="要更新Cookie的账号用户名。")
    parser_cookie.add_argument("-b", "--browser", default="chrome", choices=['chrome', 'firefox', 'edge', 'opera', 'brave', 'chromium'], help="指定从哪个浏览器获取Cookie (默认: chrome)。")
    parser_cookie.set_defaults(func=lambda args: account_manager.update_cookie_from_browser(args.account, args.browser))


    # --- 功能命令 ---
    parser_download = subparsers.add_parser("download", help="下载抖音视频。")
    parser_download.add_argument("-a", "--account", required=True, help="用于下载的抖音账号用户名。")
    parser_download.add_argument("-m", "--mode", required=True, choices=['post', 'favorite'], help="下载模式: 'post' (用户主页) 或 'favorite' (收藏)。")
    parser_download.add_argument("-u", "--user_url", help="当 mode 为 'post' 时，指定要下载的抖音用户主页URL。")
    parser_download.set_defaults(func=download_command)

    parser_upload = subparsers.add_parser("upload", help="上传视频到抖音。")
    parser_upload.add_argument("-a", "--account", required=True, help="用于上传的抖音账号用户名。")
    parser_upload.add_argument("-p", "--video_path", required=True, help="本地视频文件的完整路径。")
    parser_upload.add_argument("-t", "--title", required=True, help="视频的标题或描述。")
    parser_upload.add_argument("--tags", default="", help="视频标签，多个标签用逗号分隔，如 'Python,编程'")
    parser_upload.set_defaults(func=upload_command)

    args = parser.parse_args()
    args.func(args)

# ----------------- 命令执行函数 -----------------

def download_command(args):
    """处理 'download' 命令"""
    account_info = account_manager.get_account(args.account)
    if not account_info or not account_info.get('cookie'):
        console.print(f"[bold red]下载失败: 账号 '{args.account}' 不存在或尚未配置Cookie。[/bold red]")
        console.print(f"请先使用 'cookie' 命令为该账号获取Cookie。")
        return

    downloader = Downloader(account_info['cookie'])
    if args.mode == 'post':
        if not args.user_url:
            console.print("[bold red]错误: 'post' 模式需要提供 --user_url 参数。[/bold red]")
            return
        downloader.download_from_user_post(args.user_url)
    elif args.mode == 'favorite':
        downloader.download_from_favorites()

def upload_command(args):
    """处理 'upload' 命令"""
    account_info = account_manager.get_account(args.account)
    if not account_info:
        console.print(f"[bold red]上传失败: 指定账号 '{args.account}' 不存在。[/bold red]")
        return
    
    user_data_dir = account_info.get('user_data_dir')
    if not user_data_dir:
        console.print(f"[bold red]错误: 账号 '{args.account}' 未配置 'user_data_dir'。[/bold red]")
        return

    uploader = Uploader(user_data_dir)
    tags = [t.strip() for t in args.tags.split(',') if t.strip()] if args.tags else []

    success = uploader.upload_video(video_path=args.video_path, title=args.title, tags=tags)
    if success:
        console.print("[bold green]\n视频发布任务已成功完成。[/bold green]")
    else:
        console.print("[bold red]\n视频发布任务失败。请查看以上日志或错误截图。[/bold red]")

if __name__ == "__main__":
    main()