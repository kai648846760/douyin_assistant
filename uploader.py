# -*- coding: utf-8 -*-
# @Author: Loki Wang

import os
import time
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError
from rich.console import Console

console = Console()

class Uploader:
    """负责通过模拟浏览器操作上传视频到抖音 (使用“上传视频”按钮作为唯一正确的状态检查)"""

    def __init__(self, user_data_dir: str):
        self.user_data_dir = os.path.abspath(user_data_dir)
        os.makedirs(self.user_data_dir, exist_ok=True)
        console.print(f"[bold green]上传器初始化完成。浏览器用户数据目录: {self.user_data_dir}[/bold green]")

    def upload_video(self, video_path: str, title: str, tags: list = None):
        if not os.path.exists(video_path):
            console.print(f"[bold red]错误: 视频文件 '{video_path}' 不存在。[/bold red]")
            return False

        console.print(f"[bold blue]开始上传视频: '{os.path.basename(video_path)}'，标题: '{title}'[/bold blue]")

        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                self.user_data_dir,
                headless=False,
                args=['--disable-blink-features=AutomationControlled'],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            )
            page = browser.pages[0] if browser.pages else browser.new_page()

            try:
                # 1. 导航到上传页面
                upload_url = "https://creator.douyin.com/creator-micro/content/upload"
                console.print(f"导航到上传页面: {upload_url}")
                page.goto(upload_url, wait_until="domcontentloaded", timeout=60000)

                # 2. 循环等待那个可见的“上传视频”按钮
                upload_button_selector = page.get_by_role('button', name='上传视频')
                console.print("正在循环检查上传页面是否加载完成（标志：‘上传视频’按钮可见）...")
                
                while True:
                    if upload_button_selector.count() > 0:
                        console.print("[bold green]‘上传视频’按钮已找到，页面加载完成！[/bold green]")
                        break
                    else:
                        console.print("  [-] 未找到‘上传视频’按钮，可能正在等待登录或页面加载，2秒后重试...")
                        time.sleep(2)
                
                # 3. 使用 file_chooser 方式上传文件
                console.print(f"准备点击‘上传视频’按钮并选择文件...")
                with page.expect_file_chooser() as fc_info:
                    upload_button_selector.click()
                
                file_chooser = fc_info.value
                file_chooser.set_files(video_path)
                console.print("[bold green]文件已选择。等待页面跳转到视频编辑页...[/bold green]")

                # 4. 循环等待两种可能的编辑页URL
                while True:
                    try:
                        page.wait_for_url("**/creator-micro/content/publish**", timeout=3000)
                        console.print("[bold green]成功进入 version_1 编辑页面。[/bold green]")
                        break
                    except PlaywrightTimeoutError:
                        try:
                            page.wait_for_url("**/creator-micro/content/post/video**", timeout=3000)
                            console.print("[bold green]成功进入 version_2 编辑页面。[/bold green]")
                            break
                        except PlaywrightTimeoutError:
                            console.print("  [-] 等待进入视频编辑页面...")
                            time.sleep(0.5)

                # 5. 填写标题和话题
                console.print("正在填写标题和话题...")
                title_container_v1 = page.get_by_text('作品标题').locator("..").locator("xpath=following-sibling::div[1]").locator("input")
                time.sleep(1)
                
                if title_container_v1.count() > 0:
                    console.print("  [-] 使用方案一填写标题。")
                    title_container_v1.fill(title[:30])
                else:
                    console.print("[bold yellow]  [!] 未找到方案一，尝试备用方案二填写标题。[/bold yellow]")
                    title_container_v2 = page.locator(".notranslate")
                    title_container_v2.click()
                    page.keyboard.press("Control+KeyA")
                    page.keyboard.press("Delete")
                    page.keyboard.type(title)
                    page.keyboard.press("Enter")

                if tags:
                    tag_input_area = page.locator(".zone-container")
                    for tag in tags:
                        console.print(f"  [-] 添加话题: #{tag}")
                        tag_input_area.type("#" + tag)
                        tag_input_area.press("Space")
                
                console.print("[bold green]标题和话题填写完成。[/bold green]")

                # 6. 等待视频处理完成
                console.print("正在等待视频处理完成...")
                while True:
                    reupload_button = page.locator('[class^="long-card"] div:has-text("重新上传")')
                    if reupload_button.count() > 0:
                        console.print("[bold green]视频处理已完成。[/bold green]")
                        break
                    else:
                        console.print("  [-] 视频仍在处理中...")
                        time.sleep(2)

                # 7. 点击发布并等待最终跳转
                publish_button = page.get_by_role('button', name="发布", exact=True)
                console.print("正在点击发布按钮...")
                publish_button.click()
                
                console.print("发布按钮已点击，等待最终确认页面...")
                page.wait_for_url("**/creator-micro/content/manage**", timeout=120000)
                console.print("[bold green]视频发布成功！已跳转到作品管理页面。[/bold green]")

                time.sleep(5)
                browser.close()
                return True

            except Exception as e:
                error_msg = f"上传过程中发生未知错误: {e}"
                console.print(f"[bold red]{error_msg}[/bold red]")
                page.screenshot(path="upload_error.png")
                console.print("[bold blue]错误截图已保存为 upload_error.png[/bold blue]")
                browser.close()
                return False