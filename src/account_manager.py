# account_manager.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang

import json
import browser_cookie3
import os
from pathlib import Path
from typing import List, Dict, Optional

class AccountManager:
    """负责管理和读取 accounts.json 文件中的账号信息"""
    def __init__(self, file_path: str = None):
        if file_path is None:
            # 动态查找accounts.json文件
            self.file_path = self._find_accounts_file()
        else:
            self.file_path = file_path
        self.accounts = self._load_accounts()

    def _find_accounts_file(self) -> str:
        """查找accounts.json文件，支持多个可能的位置"""
        # 优先查找的路径
        possible_paths = [
            'accounts.json',  # 根目录
            'config/accounts.json',  # config目录
            './accounts.json',
            './config/accounts.json'
        ]

        for path in possible_paths:
            if os.path.exists(path):
                print(f"找到账号配置文件: {path}")
                return path

        # 如果都没有找到，默认在根目录创建
        print("未找到账号配置文件，将在根目录创建新的accounts.json")
        return 'accounts.json'

    def _load_accounts(self) -> List[Dict]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"提示：找不到账号文件 '{self.file_path}'，已为您创建一个新的空文件。")
            with open(self.file_path, 'w', encoding='utf-8') as f: json.dump([], f)
            return []
        except json.JSONDecodeError:
            print(f"错误：账号文件 '{self.file_path}' 格式不正确。"); return []

    def reload_accounts(self):
        """【新增】从文件中强制重新加载账号信息，解决数据同步问题"""
        print("正在从文件重载账号列表...")
        self.accounts = self._load_accounts()

    def _save_accounts(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.accounts, f, indent=2, ensure_ascii=False)
        print(f"账号信息已成功保存到 '{self.file_path}'。")

    def get_account(self, username: str) -> Optional[Dict]:
        for acc in self.accounts:
            if acc.get('username') == username: return acc
        return None

    def list_accounts(self):
        if not self.accounts: print("当前没有配置任何账号。"); return
        print("当前已配置的账号列表：")
        for i, acc in enumerate(self.accounts):
            print(f"{i+1}. 用户名: {acc.get('username')}, 备注: {acc.get('remark', '无')}")

    def add_account(self, username: str, remark: str = ""):
        if self.get_account(username): print(f"错误：用户名为 '{username}' 的账号已存在。"); return

        safe_username = username.replace(' ', '_').replace('.', '')
        user_data_dir = f"./browser_data/{safe_username}"

        # 自动创建用户数据目录
        try:
            os.makedirs(user_data_dir, exist_ok=True)
            print(f"已创建用户数据目录: {user_data_dir}")
        except Exception as e:
            print(f"警告：创建用户数据目录失败: {e}")
            # 即使创建目录失败，也继续添加账号

        new_account = {"username": username, "cookie": "", "user_data_dir": user_data_dir, "remark": remark}
        self.accounts.append(new_account)
        self._save_accounts()
        print(f"成功添加新账号 '{username}'，并自动创建了数据目录。")

    def update_cookie_from_browser(self, username: str, browser_name: str):
        account = self.get_account(username)
        if not account: print(f"错误：未在 {self.file_path} 中找到用户名为 '{username}' 的账号。"); return

        print(f"正在尝试从 '{browser_name}' 浏览器中获取 'douyin.com' 的Cookie...")
        try:
            cj_func = getattr(browser_cookie3, browser_name)
            cj = cj_func(domain_name=".douyin.com")
            cookie_str = "; ".join([f"{cookie.name}={cookie.value}" for cookie in cj])
            
            if "sessionid" not in cookie_str:
                print(f"错误：未能在 '{browser_name}' 中找到 'douyin.com' 的有效登录Cookie。"); return

            account['cookie'] = cookie_str
            self._save_accounts()
            print(f"成功为账号 '{username}' 更新Cookie！")
        except Exception as e:
            print(f"获取Cookie时发生错误: {e}")