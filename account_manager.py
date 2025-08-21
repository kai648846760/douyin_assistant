# -*- coding: utf-8 -*-
# @Author: Loki Wang

import json
import browser_cookie3
from typing import List, Dict, Optional

class AccountManager:
    """负责管理和读取 accounts.json 文件中的账号信息"""
    def __init__(self, file_path: str = 'accounts.json'):
        self.file_path = file_path
        self.accounts = self._load_accounts()

    def _load_accounts(self) -> List[Dict]:
        """从JSON文件中加载账号列表，如果文件不存在则自动创建。"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"提示：找不到账号文件 '{self.file_path}'，已为您创建一个新的空文件。")
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
            return []
        except json.JSONDecodeError:
            print(f"错误：账号文件 '{self.file_path}' 格式不正确。")
            return []

    def _save_accounts(self):
        """将当前账号列表状态保存回JSON文件。"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, indent=2, ensure_ascii=False)
        print(f"账号信息已成功保存到 '{self.file_path}'。")

    def get_account(self, username: str) -> Optional[Dict]:
        """根据用户名获取单个账号信息"""
        for acc in self.accounts:
            if acc.get('username') == username:
                return acc
        return None

    def list_accounts(self):
        """列出所有已配置的账号"""
        if not self.accounts:
            print("当前没有配置任何账号。请使用 'add-account' 命令添加。")
            return
        print("当前已配置的账号列表：")
        for i, acc in enumerate(self.accounts):
            cookie_status = "[bold green]已设置[/bold green]" if acc.get('cookie') else "[bold red]未设置[/bold red]"
            print(f"{i+1}. 用户名: {acc.get('username')}, 备注: {acc.get('remark', '无')}, Cookie状态: {cookie_status}")

    def add_account(self, username: str):
        """添加一个新的空账号配置。"""
        if self.get_account(username):
            print(f"错误：用户名为 '{username}' 的账号已存在。")
            return
        
        safe_username = username.replace(' ', '_').replace('.', '')
        
        new_account = {
            "username": username,
            "cookie": "",
            "user_data_dir": f"./browser_data/{safe_username}",
            "remark": "新账号"
        }
        self.accounts.append(new_account)
        self._save_accounts()
        print(f"成功添加新账号 '{username}'。")
        print("下一步，请使用 'cookie' 命令为其自动获取Cookie。")
        print(f"示例命令: python main.py cookie --account \"{username}\" --browser chrome")


    def update_cookie_from_browser(self, username: str, browser_name: str):
        """从本地浏览器自动获取并更新指定账号的Cookie。"""
        account = self.get_account(username)
        if not account:
            print(f"错误：未在 {self.file_path} 中找到用户名为 '{username}' 的账号。")
            return

        print(f"正在尝试从 '{browser_name}' 浏览器中获取 'douyin.com' 的Cookie...")
        
        try:
            cj_func = getattr(browser_cookie3, browser_name)
            cj = cj_func(domain_name=".douyin.com")
            
            cookie_str = "; ".join([f"{cookie.name}={cookie.value}" for cookie in cj])
            
            if "sessionid" not in cookie_str:
                print(f"[bold red]错误：未能在 '{browser_name}' 中找到 'douyin.com' 的有效登录Cookie。[/bold red]")
                print("请确保您已经通过该浏览器成功登录了抖音网页版。")
                return

            account['cookie'] = cookie_str
            self._save_accounts()
            print(f"[bold green]成功为账号 '{username}' 更新Cookie！[/bold green]")

        except AttributeError:
            print(f"错误：不支持的浏览器 '{browser_name}'。支持: chrome, firefox, edge, opera等。")
        except Exception as e:
            print(f"获取Cookie时发生错误: {e}")