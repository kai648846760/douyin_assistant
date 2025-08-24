# 🎬 抖音全能助手 (Douyin Assistant)

一个功能强大的抖音视频下载和管理工具，支持多种下载模式、批量操作和现代化GUI界面。

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-CustomTkinter-green.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/kai648846760/douyin_assistant?style=social)](https://github.com/kai648846760/douyin_assistant)

## ✨ 功能特性

### 🎯 核心功能
- ✅ **多种下载模式**：主页作品、点赞作品、收藏作品、收藏夹作品、收藏音乐、合集作品、直播下载、单个视频
- ✅ **批量下载**：支持批量下载多个作品，自动分类保存
- ✅ **视频上传**：支持批量上传视频到抖音，智能标签管理
- ✅ **多账号管理**：支持多个账号配置，自动Cookie管理
- ✅ **实时日志**：详细的操作进度和错误日志显示

### 🎨 界面特色  
- ✅ **现代化GUI**：基于CustomTkinter的深色主题界面
- ✅ **响应式设计**：支持屏幕自适应缩放，等比例布局
- ✅ **智能布局**：三选项卡设计，功能区域合理分配
- ✅ **实时反馈**：操作状态实时显示，用户体验流畅

### 🔧 技术亮点
- ✅ **uv环境管理**：使用现代化Python包管理工具
- ✅ **异步处理**：后台任务不阻塞界面操作
- ✅ **智能配置**：自动查找和管理配置文件
- ✅ **跨平台支持**：Windows、macOS完美兼容

## 🚀 快速开始

### 💾 下载预构建版本（推荐新手用户）

**🎉 最简单的方式**：直接从 [Releases](https://github.com/kai648846760/douyin_assistant/releases) 页面下载对应平台的最新版本：

- 🖥️ **Windows**: 下载 `douyin_assistant.exe` - 双击即可运行
- 🍎 **macOS**: 下载 `douyin_assistant` - 解压后运行

> **💡 为什么选择预构建版本**：
> - ✅ **零配置**：无需安装Python环境
> - ✅ **即开即用**：下载后直接运行
> - ✅ **完整依赖**：已包含所有必要组件
> - ✅ **稳定可靠**：经过自动化测试验证

### 🎨 GUI界面使用指南

启动程序后，您将看到现代化的深色主题界面，包含三个主要功能页面：

#### 👤 账号管理页面
<img width="2800" height="1838" alt="账号管理界面" src="https://github.com/user-attachments/assets/fcbc264d-9a41-4aac-b56d-0c6a9fbc4441" />

1. **添加账号**：输入账号名称和备注信息
2. **更新Cookie**：选择账号和浏览器类型，一键获取登录状态
3. **账号状态**：实时显示所有账号的配置状态

> **提示**：使用前请确保在浏览器中已经登录抖音账号

#### ⬇️ 视频下载页面
<img width="2800" height="1838" alt="视频下载界面" src="https://github.com/user-attachments/assets/98c515ea-cf9d-4afd-9f55-6664c6318af1" />

1. **选择账号**：从已配置的账号中选择一个
2. **选择模式**：
   - **主页作品**：下载指定用户的所有发布视频
   - **点赞作品**：下载您点赞过的视频
   - **收藏作品**：下载您收藏的视频
   - **单个视频**：下载指定链接的单个视频
   - 更多模式...
3. **输入链接**：根据选择的模式输入对应的抖音链接
4. **设置路径**：选择保存位置（可选，默认保存到downloads文件夹）
5. **开始下载**：点击按钮开始下载，实时查看进度

#### ⬆️ 视频上传页面
<img width="2800" height="1838" alt="视频上传界面" src="https://github.com/user-attachments/assets/aa235e1b-5afc-434e-b813-423ed023811e" />

1. **选择账号**：可多选，支持同时向多个账号上传
2. **选择视频**：点击"选择文件夹"，选择包含视频的目录
3. **设置标签**：输入通用话题标签，如"原创,教程,编程"
4. **批量上传**：程序会自动处理所有选中的视频

> **文件命名规范**：`视频标题 #标签1 #标签2.mp4`

### 📱 界面特色

- **响应式设计**：支持窗口缩放，界面元素等比例调整
- **实时反馈**：操作状态和进度实时显示在右侧日志区域
- **深色主题**：现代化UI设计，保护视力
- **智能布局**：合理的空间分配，确保所有功能区域可见

## 👨‍💻 从源码运行（开发者选项）

**适用人群**：开发者、贡献者或希望自定义修改的高级用户

### 方式一：使用uv（推荐）

```bash
# 1. 安装uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# 或者在Windows上使用PowerShell:
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. 克隆项目
git clone https://github.com/kai648846760/douyin_assistant.git
cd douyin_assistant

# 3. 自动安装依赖并运行
uv run gui_main_ctk.py  # GUI版本
uv run main.py --help  # 命令行版本
```

### 方式二：传统pip安装

```bash
# 1. 克隆项目
git clone https://github.com/kai648846760/douyin_assistant.git
cd douyin_assistant

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行程序
python gui_main_ctk.py  # GUI版本
python main.py --help   # 命令行版本
```

### 💻 环境要求

- **Python**: 3.11+ 
- **操作系统**: Windows 10+ / macOS 10.15+
- **内存**: 最少2GB可用内存
- **网络**: 稳定的网络连接

## 💻 命令行用法（高级用户选项）

**适用场景**：自动化脚本、批量处理、服务器环境或偏好命令行的高级用户

### 1. 账号管理

```bash
# 列出所有账号
uv run main.py list

# 添加新账号
uv run main.py add-account -u "账号名称" --remark "备注信息"

# 更新Cookie
uv run main.py cookie -a "账号名称" -b chrome
```

### 2. 视频下载

```bash
# 下载主页作品
uv run main.py download -a "账号名称" -m post -u "https://www.douyin.com/user/xxx"

# 下载点赞作品
uv run main.py download -a "账号名称" -m like

# 下载单个视频
uv run main.py download -a "账号名称" -m one -u "https://www.douyin.com/video/xxx"
```

### 3. 视频上传

```bash
# 上传单个视频
uv run main.py upload -a "账号名称" -p "video.mp4" -t "视频标题" --tags "标签1,标签2"

# 批量上传目录
uv run main.py batch-upload -a "账号名称" -d "videos/" --tags "原创,教程"
```

## ⚙️ 配置说明

### accounts.json 结构
账号配置文件位于 `config/accounts.json`，自动生成且支持多种格式：

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

### 目录结构说明
- **downloads/**: 默认下载目录，按类型自动分类
- **browser_data/**: 浏览器数据目录，每个账号独立存储
- **config/**: 配置文件目录，包含账号信息和应用设置

### 支持的浏览器
- **Chrome** / **Chromium** （推荐）
- **Firefox**
- **Edge**
- **Opera**
- **Brave**

> **提示**：使用前请确保在相应浏览器中已经登录抖音账号。

## 🧐 版本选择指南

| 用户类型 | 推荐方式 | 优劣势 | 适用场景 |
|----------|---------|---------|---------|
| 👶 **新手用户** | [Releases 下载](https://github.com/kai648846760/douyin_assistant/releases) | ✅ 零配置、即开即用<br>❌ 无法自定义 | 日常使用、不需修改 |
| 👨‍💻 **开发者** | uv run / pip install | ✅ 可修改、更新快<br>❌ 需配置环境 | 二次开发、Bug修复 |
| ⚙️ **高级用户** | 命令行模式 | ✅ 批量操作、自动化<br>❌ 学习成本 | Windows/macOS脚本集成 |

---

## 📁 项目结构

```
douyin_assistant/
├── src/                     # 核心代码目录
│   ├── main.py              # 命令行主逻辑
│   ├── main_window_ctk.py   # CustomTkinter GUI主界面
│   ├── main_window.py       # PySide6 GUI界面（旧版）
│   ├── worker_ctk.py        # 后台任务处理器
│   ├── account_manager.py   # 账号管理模块
│   ├── downloader.py        # 下载核心逻辑
│   ├── uploader.py          # 上传功能模块
│   ├── xbogus.py           # ABogus算法实现
│   └── api_endpoints.py     # API端点定义
├── config/                 # 配置文件目录
│   ├── accounts.json        # 账号配置文件
│   └── config.py           # 应用配置
├── browser_data/           # 浏览器数据（自动创建）
├── downloads/              # 下载文件存储
├── main.py                # 命令行入口
├── gui_main_ctk.py        # CustomTkinter GUI入口
├── gui_main.py            # PySide6 GUI入口（旧版）
├── pyproject.toml         # 项目配置文件
├── requirements.txt       # Python依赖列表
├── icon.ico              # 程序图标
└── README.md              # 项目说明文档
```

## 🔧 高级功能

### 操作模式详解

| 模式 | 描述 | 是否需要URL | 登录要求 |
|------|------|-------------|----------|
| `post` | 主页作品 | ✅ | 可选 |
| `like` | 点赞作品 | ❌ | ✅ |
| `collection` | 收藏作品 | ❌ | ✅ |
| `collects` | 收藏夹作品 | ✅ | ✅ |
| `music` | 收藏音乐 | ✅ | ✅ |
| `mix` | 合集作品 | ✅ | 可选 |
| `live` | 直播下载 | ✅ | 可选 |
| `one` | 单个视频 | ✅ | 可选 |

### 批量上传规则

1. **文件命名格式**：
   ```
   视频标题 #标签1 #标签2 #标签3.mp4
   ```

2. **支持的视频格式**：
   - `.mp4` （推荐）
   - `.mov`
   - `.webm` 
   - `.avi`

3. **上传策略**：
   - 支持多账号同时上传
   - 自动间隔控制，防止被限制
   - 智能错误重试机制

## 🛡️ 注意事项

- ℹ️ **合理使用**：请遵守抖音平台的使用协议和相关法律法规
- ℹ️ **频率控制**：建议合理控制下载和上传频率，避免账号被限制
- ℹ️ **数据备份**：建议定期备份 `config/accounts.json` 和 `browser_data/` 目录
- ℹ️ **版权意识**：下载的内容仅供个人学习使用，请尊重原作者版权

## 📊 性能优化

- **并发下载**：支持多线程并发，提高下载效率
- **断点续传**：支持下载中断后续传
- **智能去重**：自动检测并跳过已存在的文件
- **内存优化**：适配不同配置的设备，支持低内存运行

## 🔍 故障排除

### 常见问题

**Q: 提示"Cookie无效"或登录失败？**
A: 
1. 确保在浏览器中已成功登录抖音
2. 关闭所有浏览器窗口后重新获取Cookie
3. 尝试使用不同的浏览器（如Chrome、Edge）

**Q: 下载速度过慢或经常失败？**
A:
1. 检查网络连接稳定性
2. 适当减少并发数量
3. 使用代理或VPN改善网络环境

**Q: 上传视频失败或被拒绝？**
A:
1. 确保视频格式和尺寸符合平台要求
2. 检查账号是否有上传权限
3. 避免频繁上传，遵守平台限制

### 日志文件
程序运行过程中的详细日志会在GUI界面中实时显示，帮助您诊断和解决问题。

## 📦 程序分发

### 🎉 预构建版本（强烈推荐）

**💪 为什么选择预构建版本？**

我们提供了完全自动化的构建流程，使用 GitHub Actions 为您打包好了各平台的可执行文件：

- **⚡ 极速体验**：下载后立即使用，无需等待环境配置
- **🛡️ 稳定可靠**：经过完整自动化测试验证的稳定版本
- **🌍 全平台支持**：Windows、macOS 双平台同步发布
- **📦 零依赖**：单文件包含所有必要组件，无需Python环境
- **🔄 自动更新**：每次发布新版本时自动构建最新版本

> **🚀 立即下载**：[前往 Releases 页面](https://github.com/kai648846760/douyin_assistant/releases) 获取最新版本

**📥 各平台下载指南**：
- 🖥️ **Windows用户**：下载 `douyin_assistant.exe`，双击运行
- 🍎 **macOS用户**：下载 `douyin_assistant`，解压后运行

### 🔧 自定义构建（仅限开发者）

> ⚠️ **注意**：只有在需要修改源码或定制功能时才建议自行构建

如果您是开发者并需要自定义构建：

## 🙏 致谢

本项目参考了以下优秀的开源项目：
- [F2 项目](https://github.com/chen310/f2) - 抖音数据获取
- [Social Auto Upload](https://github.com/dreammis/social-auto-upload) - 社交媒体自动化
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - 现代化GUI框架

## 📝 更新日志

### v2.0.0 (当前版本)
- ✨ 全新CustomTkinter现代化界面
- ✨ 响应式屏幕适配设计
- ✨ 优化的布局管理系统
- ✨ 改进的账号管理功能
- ✨ 增强的错误处理机制
- ✨ uv包管理工具支持

### v1.0.0
- 🎉 初始版本发布
- 📥 多种下载模式支持
- 📤 批量上传功能
- 👥 多账号管理
- 🖥️ PySide6 GUI界面

## 🤝 贡献指南

欢迎贡献代码或提出建议！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发环境设置
```bash
# 使用uv设置开发环境
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows
uv pip install -r requirements.txt
```

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## ⭐ Star 支持

如果这个项目对您有帮助，请给一个 ⭐ Star 以表示支持！您的支持是我们持续改进的动力。

[![Star History Chart](https://api.star-history.com/svg?repos=kai648846760/douyin_assistant&type=Date)](https://star-history.com/#kai648846760/douyin_assistant&Date)

---

<div align="center">
  <strong>🎬 抖音全能助手 - 让视频管理更简单</strong><br>
  <em>Powered by Loki Wang</em>
</div>
