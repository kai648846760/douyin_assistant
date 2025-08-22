# 抖音全能助手 (Douyin Assistant)

一个功能强大的抖音视频下载和管理工具，支持多种下载模式和批量操作。

## 🚀 功能特性

- ✅ **多种下载模式**：主页作品、点赞作品、收藏作品、收藏夹作品、收藏音乐、合集作品、直播下载、单个视频
- ✅ **批量下载**：支持批量下载多个作品
- ✅ **账号管理**：支持多个账号配置
- ✅ **视频上传**：支持批量上传视频到抖音
- ✅ **实时日志**：详细的下载进度和错误日志
- ✅ **GUI界面**：用户友好的图形界面

## 🛠️ 安装和使用

### 环境要求
- Python 3.8+
- PySide6 (GUI界面需要)
- 其他依赖见 `requirements.txt`

### 安装步骤

1. **安装依赖**

   **方式一：使用 pip**
   ```bash
   pip install -r requirements.txt
   ```

   **方式二：使用 uv（推荐）**
   ```bash
   # 安装 uv
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # 使用 uv 安装依赖
   uv pip install -r requirements.txt
   ```

2. **运行程序**

   **命令行版本：**
   ```bash
   python main.py --help
   python main.py list
   ```

   **GUI版本：**
   ```bash
   python gui_main.py
   ```

## 📋 使用说明

### 1. 账号管理
```bash
# 列出所有已配置的账号
python main.py list

# 添加新账号
python main.py add-account -u "账号名称" --remark "备注信息"

# 从浏览器获取Cookie
python main.py cookie -a "账号名称" -b chrome
```

### 2. 视频下载
```bash
# 下载主页作品
python main.py download -a "账号名称" -m post -u "https://www.douyin.com/user/xxx"

# 下载收藏作品
python main.py download -a "账号名称" -m collection

# 下载单个视频
python main.py download -a "账号名称" -m one -u "https://www.douyin.com/video/xxx"
```

### 3. 视频上传
```bash
# 上传单个视频
python main.py upload -a "账号名称" -p "video.mp4" -t "视频标题" --tags "标签1,标签2"

# 批量上传
python main.py batch-upload -a "账号名称" -d "videos/" --tags "原创"
```

### 4. GUI使用
```bash
python gui_main.py
```
然后在图形界面中进行操作：
- 管理账号：添加账号、更新Cookie
- 下载视频：选择模式、输入URL、开始下载
- 上传视频：选择视频文件、设置参数、批量上传

## ⚙️ 配置说明

### accounts.json 结构
```json
[
  {
    "username": "账号名称",
    "cookie": "cookie字符串",
    "user_data_dir": "./browser_data/账号名称",
    "remark": "备注信息"
  }
]
```

### 下载路径
- 默认下载到 `downloads/` 目录
- 可以通过参数指定自定义路径
- 不同类型的内容会自动分类到子目录

## 🔧 命令行参数

### 通用参数
- `-h, --help` - 显示帮助信息
- `-a, --account` - 指定使用的账号
- `-u, --url` - 目标URL（某些模式需要）

### 下载模式参数
- `post` - 主页作品（需要URL）
- `like` - 点赞作品
- `collection` - 收藏作品
- `collects` - 收藏夹作品（需要URL）
- `music` - 收藏音乐（需要URL）
- `mix` - 合集作品（需要URL）
- `live` - 直播下载（需要URL）
- `one` - 单个视频（需要URL）

### 上传参数
- `-p, --video_path` - 视频文件路径
- `-t, --title` - 视频标题
- `--tags` - 标签（逗号分隔）

## 📁 项目结构

```
/douyin_assistant/
├── src/                    # 主应用程序代码
│   ├── main.py            # 命令行主逻辑
│   ├── main_window.py     # GUI主界面
│   ├── worker.py          # 后台工作线程
│   ├── downloader.py      # 下载核心逻辑
│   ├── uploader.py        # 上传功能
│   ├── account_manager.py # 账号管理
│   ├── gui.py             # GUI组件
│   ├── xbogus.py          # ABogus算法
│   └── api_endpoints.py   # API端点定义
├── config/                # 配置文件
│   ├── config.py          # 应用配置
│   └── accounts.json      # 账号配置
├── downloads/             # 下载的文件
├── main.py               # 命令行入口
├── gui_main.py           # GUI入口
├── requirements.txt      # Python依赖
└── README.md             # 项目说明
```

## 🙏 致谢

本项目参考了以下开源项目：
- [F2 项目](https://github.com/chen310/f2) 
- [Social Auto Upload](https://github.com/dreammis/social-auto-upload)

## 📝 更新日志

### v1.0.0
- 初始版本发布
- 支持多种下载模式
- GUI界面优化
- ABogus算法集成
- 智能配置文件管理

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📄 许可证

本项目暂时采用 [MIT License](LICENSE) 开源许可证。

## ⭐ Star 支持

如果这个项目对您有帮助，请给一个 ⭐ Star 以表示支持！


[![Star History Chart](https://api.star-history.com/svg?repos=kai648846760/douyin_assistant&type=Date)](https://star-history.com/#kai648846760/douyin_assistant&Date)