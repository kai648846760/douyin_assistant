# -*- coding: utf-8 -*-
# @Author: Loki Wang

import os
import time
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeoutError
from rich.console import Console

console = Console()

class Uploader:
    """
    负责通过模拟浏览器操作上传视频到抖音。
    【最终稳定版】: 放弃了不可靠的无头模式，回归最稳定的有头模式，确保用户数据能被正确加载和识别。
    """

    def __init__(self, user_data_dir: str):
        self.user_data_dir = os.path.abspath(user_data_dir)
        os.makedirs(self.user_data_dir, exist_ok=True)
        console.print(f"[bold green]上传器初始化完成。浏览器用户数据目录: {self.user_data_dir}[/bold green]")

    def upload_video(self, video_path: str, title: str, tags: list = None):
        if not os.path.exists(video_path):
            console.print(f"[bold red]错误: 视频文件 '{video_path}' 不存在。[/bold red]")
            return False

        console.print(f"[bold blue]开始上传任务: '{os.path.basename(video_path)}'[/bold blue]")

        with sync_playwright() as p:
            console.print("[yellow]正在启动浏览器... (使用有头模式确保登录状态被正确识别)[/yellow]")
            browser = p.chromium.launch_persistent_context(
                self.user_data_dir,
                headless=False, # 永远使用有头模式，这是最可靠的方式
                args=['--disable-blink-features=AutomationControlled'],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            )
            page = browser.pages[0] if browser.pages else browser.new_page()

            try:
                # 1. 导航到上传页面
                upload_url = "https://creator.douyin.com/creator-micro/content/upload"
                home_url_fragment = "/creator-micro/home"
                
                console.print(f"导航到上传页面: {upload_url}")
                page.goto(upload_url, wait_until="domcontentloaded", timeout=60000)

                # 2. 采用我们最终验证成功的智能等待逻辑
                console.print("正在检查登录状态或等待您登录...")
                
                while True:
                    # 检查点1：上传按钮是否存在 (说明已经在上传页)
                    upload_button = page.get_by_role('button', name='上传视频')
                    if upload_button.count() > 0:
                        console.print("[bold green]‘上传视频’按钮已找到，您已登录！[/bold green]")
                        break
                    
                    # 检查点2：URL是否已经跳转到主页 (说明登录成功了)
                    if home_url_fragment in page.url:
                        console.print(f"[bold green]检测到已跳转到创作者主页，登录成功！[/bold green]")
                        break
                    
                    # 如果两个都不是，说明还在登录页，继续等待
                    console.print("  [-] 未检测到登录成功信号，正在等待您扫码登录，5秒后重试...")
                    time.sleep(5)
                
                # 3. 确保我们最终在上传页面上
                if upload_url not in page.url:
                    console.print(f"当前在主页，正在跳转到上传页面...")
                    page.goto(upload_url, wait_until="domcontentloaded")
                    upload_button = page.get_by_role('button', name='上传视频')
                    upload_button.wait_for(state="visible", timeout=30000)

                # 4. 上传文件
                console.print(f"准备点击‘上传视频’按钮并选择文件...")
                with page.expect_file_chooser() as fc_info:
                    upload_button.click()
                
                file_chooser = fc_info.value
                file_chooser.set_files(video_path)
                console.print("[bold green]文件已选择。等待页面跳转到视频编辑页...[/bold green]")

                # --- 后续所有流程均与之前最终稳定版相同 ---
                while True:
                    try:
                        page.wait_for_url("**/creator-micro/content/publish**", timeout=3000)
                        break
                    except PlaywrightTimeoutError:
                        try:
                            page.wait_for_url("**/creator-micro/content/post/video**", timeout=3000)
                            break
                        except PlaywrightTimeoutError:
                            time.sleep(0.5)

                title_container_v1 = page.get_by_text('作品标题').locator("..").locator("xpath=following-sibling::div[1]").locator("input")
                time.sleep(1)
                
                if title_container_v1.count() > 0:
                    title_container_v1.fill(title[:30])
                else:
                    title_container_v2 = page.locator(".notranslate")
                    title_container_v2.click()
                    page.keyboard.press("Control+KeyA")
                    page.keyboard.press("Delete")
                    page.keyboard.type(title)
                    page.keyboard.press("Enter")

                if tags:
                    tag_input_area = page.locator(".zone-container")
                    for tag in tags:
                        tag_input_area.type("#" + tag)
                        tag_input_area.press("Space")
                
                while True:
                    if page.locator('[class^="long-card"] div:has-text("重新上传")').count() > 0:
                        break
                    else:
                        time.sleep(2)

                page.get_by_role('button', name="发布", exact=True).click()
                
                page.wait_for_url("**/creator-micro/content/manage**", timeout=120000)
                console.print("[bold green]视频发布成功！[/bold green]")

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