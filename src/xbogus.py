# xbogus.py
# -*- coding: utf-8 -*-
# @Author: Loki Wang

import time
import base64
import hashlib
from urllib.parse import urlencode

class XBogus:
    def __init__(self, user_agent: str = "") -> None:
        # fmt: off
        self.Array = [
            None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, None, None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None, None, None, 10, 11, 12, 13, 14, 15
        ]
        self.character = "Dkdpgh4ZKsQB80/Mfvw36XI1R25-WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe="
        # fmt: on
        self.ua_key = b"\x00\x01\x0c"
        self.user_agent = (
            user_agent
            if user_agent is not None and user_agent != ""
            else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
        )

    def md5_str_to_array(self, md5_str):
        if isinstance(md5_str, str) and len(md5_str) > 32:
            return [ord(char) for char in md5_str]
        else:
            array = []
            idx = 0
            while idx < len(md5_str):
                char1 = md5_str[idx]
                char2 = md5_str[idx + 1] if idx + 1 < len(md5_str) else '0'

                # 确保索引在Array范围内，并处理None值
                idx1 = ord(char1) if ord(char1) < len(self.Array) else ord(char1) % len(self.Array)
                idx2 = ord(char2) if ord(char2) < len(self.Array) else ord(char2) % len(self.Array)

                val1 = self.Array[idx1] if self.Array[idx1] is not None else 0
                val2 = self.Array[idx2] if self.Array[idx2] is not None else 0

                array.append((val1 << 4) | val2)
                idx += 2
            return array

    def md5_encrypt(self, url_params):
        hashed_url_params = self.md5_str_to_array(
            self.md5(self.md5_str_to_array(self.md5(url_params)))
        )
        return hashed_url_params

    def md5(self, input_data):
        if isinstance(input_data, str):
            array = self.md5_str_to_array(input_data)
        elif isinstance(input_data, list):
            array = input_data
        else:
            raise ValueError("Invalid input type. Expected str or list.")
        md5_hash = hashlib.md5()
        md5_hash.update(bytes(array))
        return md5_hash.hexdigest()

    def encoding_conversion(self, a, b, c, e, d, t, f, r, n, o, i, _, x, u, s, l, v, h, p):
        y = [a]
        y.append(int(i))
        y.extend([b, _, c, x, e, u, d, s, t, l, f, v, r, h, n, p, o])
        return bytes(y).decode("ISO-8859-1")

    def encoding_conversion2(self, a, b, c):
        return chr(a) + chr(b) + c

    def rc4_encrypt(self, key, data):
        S = list(range(256))
        j = 0
        encrypted_data = bytearray()
        for i in range(256):
            j = (j + S[i] + key[i % len(key)]) % 256
            S[i], S[j] = S[j], S[i]
        i = j = 0
        for byte in data:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            encrypted_byte = byte ^ S[(S[i] + S[j]) % 256]
            encrypted_data.append(encrypted_byte)
        return encrypted_data

    def calculation(self, a1, a2, a3):
        x1 = (a1 & 255) << 16
        x2 = (a2 & 255) << 8
        x3 = x1 | x2 | a3
        return (
            self.character[(x3 & 16515072) >> 18]
            + self.character[(x3 & 258048) >> 12]
            + self.character[(x3 & 4032) >> 6]
            + self.character[x3 & 63]
        )

    def get_xbogus(self, url_params: str) -> tuple:
        array1 = self.md5_str_to_array(
            self.md5(
                base64.b64encode(
                    self.rc4_encrypt(self.ua_key, self.user_agent.encode("ISO-8859-1"))
                ).decode("ISO-8859-1")
            )
        )
        array2 = self.md5_str_to_array(
            self.md5(self.md5_str_to_array("d41d8cd98f00b204e9800998ecf8427e"))
        )
        url_params_array = self.md5_encrypt(url_params)
        timer = int(time.time())
        ct = 536919696
        array3 = []
        array4 = []
        xb_ = ""
        # fmt: off
        new_array = [
            64, 0, 1, 12,  # 修复：将float改为int，使用0代替0.00390625
            url_params_array[14], url_params_array[15], array2[14], array2[15], array1[14], array1[15],
            timer >> 24 & 255, timer >> 16 & 255, timer >> 8 & 255, timer & 255,
            ct >> 24 & 255, ct >> 16 & 255, ct >> 8 & 255, ct & 255
        ]
        # fmt: on
        xor_result = new_array[0]
        for i in range(1, len(new_array)):
            # 确保值不为None
            val = new_array[i] if new_array[i] is not None else 0
            xor_result ^= val

        new_array.append(xor_result)

        idx = 0
        while idx < len(new_array):
            array3.append(new_array[idx])
            try:
                array4.append(new_array[idx + 1])
            except IndexError:
                pass
            idx += 2

        merge_array = array3 + array4

        garbled_code = self.encoding_conversion2(
            2,
            255,
            self.rc4_encrypt(
                "ÿ".encode("ISO-8859-1"),
                self.encoding_conversion(*merge_array).encode("ISO-8859-1"),
            ).decode("ISO-8859-1"),
        )

        idx = 0
        while idx < len(garbled_code):
            xb_ += self.calculation(
                ord(garbled_code[idx]),
                ord(garbled_code[idx + 1]),
                ord(garbled_code[idx + 2]),
            )
            idx += 3
        
        final_url_params = f"{url_params}&X-Bogus={xb_}"
        return (final_url_params, xb_)

    def get_xbogus_url(self, url: str) -> str:
        url_params = url.split("?")[1]
        base_url = url.split("?")[0]
        signed_params, _ = self.get_xbogus(url_params)
        return f"{base_url}?{signed_params}"

class ABogusManager:
    """ABogus参数管理器，基于F2项目实现"""

    @staticmethod
    def str_2_endpoint(user_agent: str, param_str: str) -> str:
        """将参数字符串转换为带有ABogus参数的URL"""
        try:
            xbogus = XBogus(user_agent)
            signed_params, xb_value = xbogus.get_xbogus(param_str)
            # 将X-Bogus替换为a_bogus，因为抖音API使用的是a_bogus参数
            signed_params_with_abogus = signed_params.replace(f"X-Bogus={xb_value}", f"a_bogus={xb_value}")
            return f"?{signed_params_with_abogus}"
        except Exception as e:
            print(f"ABogus参数生成失败: {e}")
            return f"?{param_str}"

    @staticmethod
    def generate_abogus_params(user_agent: str, base_params: dict) -> dict:
        """生成带有ABogus参数的完整参数字典"""
        try:
            param_str = urlencode(base_params)
            signed_url = ABogusManager.str_2_endpoint(user_agent, param_str)

            # 解析生成的URL参数
            if "?" in signed_url:
                query_part = signed_url.split("?", 1)[1]
                params = {}
                for pair in query_part.split("&"):
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        params[key] = value
                return params
            else:
                return base_params
        except Exception as e:
            print(f"ABogus参数生成失败: {e}")
            return base_params
