# -*- coding: utf-8 -*-
# @Author: Loki Wang

import os
import time
import argparse
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

# 从其他模块导入核心类
from account_manager import AccountManager
from downloader import Downloader
from uploader import Uploader

# --- 全局常量和初始化 ---

# 初始化 rich 库，用于美观的命令行输出
console = Console()
# 实例化账号管理器，项目启动时即加载 accounts.json
account_manager = AccountManager()
# 定义支持批量上传的视频文件扩展名列表
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.webm', '.avi')


def print_welcome_message():
    """打印风格化的欢迎信息"""
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
    """主函数：解析命令行参数并分发任务"""
    print_welcome_message()

    # --- 命令行参数解析器设置 ---
    parser = argparse.ArgumentParser(description="抖音全能助手 - 自动管理账号，轻松爬取与发布。")
    # 创建子命令解析器，确保用户必须选择一个操作
    subparsers = parser.add_subparsers(dest="command", help="选择一个命令", required=True)

    # --- 账号管理命令定义 ---
    # `list` 命令
    parser_list = subparsers.add_parser("list", help="列出所有已配置的抖音账号及其状态。")
    parser_list.set_defaults(func=lambda args: account_manager.list_accounts())
    
    # `add-account` 命令
    parser_add = subparsers.add_parser("add-account", help="添加一个新的账号配置。")
    parser_add.add_argument("-u", "--username", required=True, help="要添加的新账号的唯一用户名（例如 '我的大号'）。")
    parser_add.set_defaults(func=lambda args: account_manager.add_account(args.username))

    # `cookie` 命令
    parser_cookie = subparsers.add_parser("cookie", help="从本地浏览器自动获取并更新指定账号的Cookie。")
    parser_cookie.add_argument("-a", "--account", required=True, help="要更新Cookie的账号用户名。")
    parser_cookie.add_argument("-b", "--browser", default="chrome", choices=['chrome', 'firefox', 'edge', 'opera', 'brave', 'chromium'], help="指定从哪个浏览器获取Cookie (默认: chrome)。")
    parser_cookie.set_defaults(func=lambda args: account_manager.update_cookie_from_browser(args.account, args.browser))

    # --- 功能命令定义 ---
    # `download` 命令
    parser_download = subparsers.add_parser("download", help="下载抖音视频。")
    parser_download.add_argument("-a", "--account", required=True, help="用于下载的抖音账号用户名。")
    parser_download.add_argument("-m", "--mode", required=True, choices=['post', 'favorite', 'collection'], help="下载模式: 'post' (用户主页), 'favorite' (收藏), 'collection' (合集)。")
    parser_download.add_argument("-u", "--url", help="当 mode 为 'post' 或 'collection' 时，指定目标URL。")
    parser_download.set_defaults(func=download_command)

    # `upload` 命令 (单个视频)
    parser_upload = subparsers.add_parser("upload", help="上传单个视频到抖音。")
    parser_upload.add_argument("-a", "--account", required=True, help="用于上传的抖音账号用户名。")
    parser_upload.add_argument("-p", "--video_path", required=True, help="本地视频文件的完整路径。")
    parser_upload.add_argument("-t", "--title", required=True, help="视频的标题或描述。")
    parser_upload.add_argument("--tags", default="", help="视频标签，多个标签用逗号分隔，如 'Python,编程'")
    parser_upload.set_defaults(func=upload_command)

    # `batch-upload` 命令 (批量上传)
    parser_batch_upload = subparsers.add_parser("batch-upload", help="批量上传指定目录下的所有视频。")
    parser_batch_upload.add_argument("-a", "--account", required=True, help="用于上传的抖音账号用户名。")
    parser_batch_upload.add_argument("-d", "--dir_path", required=True, help="包含视频文件的目录路径。")
    parser_batch_upload.add_argument("--tags", default="", help="为所有视频添加的通用标签，多个用逗号分隔。")
    parser_batch_upload.set_defaults(func=batch_upload_command)

    # 解析用户输入的参数
    args = parser.parse_args()
    # 根据用户选择的命令，调用对应的处理函数
    args.func(args)

# ----------------- 命令执行函数 -----------------

def download_command(args):
    """处理 'download' 命令的逻辑"""
    # 验证账号是否存在且已配置Cookie
    account_info = account_manager.get_account(args.account)
    if not account_info or not account_info.get('cookie'):
        console.print(f"[bold red]下载失败: 账号 '{args.account}' 不存在或尚未配置Cookie。[/bold red]")
        return
    
    # 实例化下载器
    downloader = Downloader(account_info['cookie'])
    
    # 根据不同的下载模式调用不同的方法
    if args.mode == 'post':
        if not args.url:
            console.print("[bold red]错误: 'post' 模式需要提供 --url 参数。[/bold red]")
            return
        downloader.download_from_user_post(args.url)
    elif args.mode == 'favorite':
        downloader.download_from_favorites()
    elif args.mode == 'collection':
        if not args.url:
            console.print("[bold red]错误: 'collection' 模式需要提供 --url 参数。[/bold red]")
            return
        downloader.download_from_collection(args.url)

def upload_command(args):
    """处理 'upload' (单个上传) 命令的逻辑"""
    # 验证账号是否存在
    account_info = account_manager.get_account(args.account)
    if not account_info:
        console.print(f"[bold red]上传失败: 指定账号 '{args.account}' 不存在。[/bold red]")
        return
    
    # 验证账号是否配置了 user_data_dir
    user_data_dir = account_info.get('user_data_dir')
    if not user_data_dir:
        console.print(f"[bold red]错误: 账号 '{args.account}' 未配置 'user_data_dir'。[/bold red]")
        return
    
    # 实例化上传器
    uploader = Uploader(user_data_dir)
    # 解析标签字符串为列表
    tags = [t.strip() for t in args.tags.split(',') if t.strip()] if args.tags else []
    
    # 执行上传
    success = uploader.upload_video(video_path=args.video_path, title=args.title, tags=tags)
    
    # 打印最终结果
    if success:
        console.print("[bold green]\n视频发布任务已成功完成。[/bold green]")
    else:
        console.print("[bold red]\n视频发布任务失败。[/bold red]")

def batch_upload_command(args):
    """处理 'batch-upload' (批量上传) 命令的逻辑"""
    # 验证账号和 user_data_dir
    account_info = account_manager.get_account(args.account)
    if not account_info:
        console.print(f"[bold red]批量上传失败: 指定账号 '{args.account}' 不存在。[/bold red]")
        return
    user_data_dir = account_info.get('user_data_dir')
    if not user_data_dir:
        console.print(f"[bold red]错误: 账号 '{args.account}' 未配置 'user_data_dir'。[/bold red]")
        return

    # 验证提供的路径是否是一个有效的目录
    if not os.path.isdir(args.dir_path):
        console.print(f"[bold red]错误: 提供的路径 '{args.dir_path}' 不是一个有效的目录。[/bold red]")
        return

    # 扫描目录，根据扩展名筛选视频文件
    video_files = [f for f in os.listdir(args.dir_path) if f.lower().endswith(VIDEO_EXTENSIONS)]
    if not video_files:
        console.print(f"[bold yellow]在目录 '{args.dir_path}' 中没有找到任何支持的视频文件。[/bold yellow]")
        return

    console.print(f"[bold cyan]发现 {len(video_files)} 个视频待上传。即将开始批量任务...[/bold cyan]")
    
    # 实例化上传器和解析通用标签
    uploader = Uploader(user_data_dir)
    common_tags = [t.strip() for t in args.tags.split(',') if t.strip()] if args.tags else []
    
    success_count, fail_count = 0, 0

    # 遍历所有找到的视频文件
    for i, filename in enumerate(video_files):
        video_path = os.path.join(args.dir_path, filename)
        console.print(Panel(f"[bold]任务 {i+1}/{len(video_files)}: 正在处理 '{filename}'[/bold]", border_style="blue"))
        
        # --- 从文件名解析标题和标签 ---
        # 约定格式: "这是视频标题 #标签1 #标签2.mp4"
        base_name = os.path.splitext(filename)[0]
        parts = base_name.split('#')
        video_title = parts[0].strip()
        filename_tags = [tag.strip() for tag in parts[1:] if tag.strip()]
        
        # 合并通用标签和从文件名解析出的标签
        final_tags = common_tags + filename_tags

        console.print(f"  [>] 视频路径: {video_path}")
        console.print(f"  [>] 解析标题: {video_title}")
        console.print(f"  [>] 合成标签: {final_tags}")

        # 调用 uploader 上传单个视频
        success = uploader.upload_video(video_path=video_path, title=video_title, tags=final_tags)
        
        if success:
            success_count += 1
            console.print(f"[bold green]'{filename}' 上传成功。[/bold green]")
        else:
            fail_count += 1
            console.print(f"[bold red]'{filename}' 上传失败。详情请查看上方日志。[/bold red]")
        
        # 在两次上传之间暂停，模仿人类行为，避免触发平台的风控
        if i < len(video_files) - 1:
            console.print("[yellow]暂停10秒，准备下一个任务...[/yellow]")
            time.sleep(10)

    # 打印最终的批量任务总结
    console.print(Panel(f"[bold]批量上传任务完成！\n成功: {success_count} 个\n失败: {fail_count} 个[/bold]", border_style="green"))


# 当脚本作为主程序运行时，执行 main 函数
if __name__ == "__main__":
    main()