# 抖音全能助手 (Douyin All-in-One Assistant)

**✨ `uv` Powered ✨**

---

## 核心功能

*   **强大的账号管理系统**
    *   命令行快速 **添加/列出** 账号配置。
    *   **一键自动获取/更新** 本地已登录浏览器的Cookie，彻底告别手动复制。
*   **无水印视频下载**
    *   支持下载指定用户的**主页所有作品**。
    *   支持下载自己账号的**所有收藏视频**。
*   **自动化视频发布**
    *   **多账号上传**：为每个账号保持独立的登录会话，一次扫码，永久有效。
    *   **智能等待**：自动检测登录状态，提示用户扫码并耐心等待，确保流程顺畅。
    *   **稳定可靠**：基于对成功项目的深入分析，采用最稳健的页面元素定位和状态判断逻辑。
    *   **功能丰富**：支持自定义视频标题和多个话题标签。

---

## 🚀 安装指南 (基于 uv)

### 1. 环境准备
*   确保您已安装 Python 3.8 或更高版本。
*   **安装 `uv`**: 如果您尚未安装 `uv`，请根据您的操作系统执行以下命令：

    *   **macOS / Linux**:
        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```
    *   **Windows**:
        ```bash
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        ```

### 2. 克隆并进入项目
```bash
# 如果您使用git
git clone <your_project_repo_url>
cd douyou_assistant

# 或者直接解压项目文件夹并进入
cd path/to/douyou_assistant
```

### 3. 使用 `uv` 创建并激活虚拟环境
`uv` 可以极速创建虚拟环境。
```bash
uv venv
```
*   此命令会在当前目录下创建一个名为 `.venv` 的虚拟环境。
*   **激活环境** (此步骤与原生`venv`相同):
    *   **Windows**:
        ```bash
        .\.venv\Scripts\activate
        ```
    *   **macOS / Linux**:
        ```bash
        source .venv/bin/activate
        ```
    *(成功激活后，你的命令行提示符前会出现 `(.venv)`)*

### 4. 使用 `uv` 安装项目依赖
体验 `uv` 的闪电般的安装速度！
```bash
uv pip install -r requirements.txt
```

### 5. 安装 Playwright 浏览器核心 (至关重要！)
此命令由 Playwright 包提供，保持不变。
```bash
playwright install
```

---

## 🛠️ 配置与账号管理

本项目的账号管理已完全命令行化，您无需手动编辑 `accounts.json` 文件。

### 1. 添加一个新账号
这是您的第一步。为您的账号取一个好记的名称（例如 "我的大号"）。
```bash
python main.py add-account --username "我的大号"
```
*   **作用**：此命令会在 `accounts.json` 文件中为您创建一个配置模板，并自动分配一个用于保持登录状态的文件夹。

### 2. 为账号自动获取Cookie
Cookie 主要用于视频下载。请先在您的电脑浏览器（如Chrome）上登录一次抖音。
```bash
# --browser 参数可选, 支持 chrome, firefox, edge 等, 默认为 chrome
python main.py cookie --account "我的大号" --browser chrome
```
*   **作用**：此命令会自动从您电脑的Chrome浏览器中读取抖音的登录Cookie，并更新到 `accounts.json` 文件中。

### 3. 查看已配置的账号
您可以随时查看当前管理的所有账号及其状态。
```bash
python main.py list
```

---

## 📖 使用指南 (命令参考)

### `list` - 列出账号
*   **功能**: 显示所有已配置的账号及其Cookie状态。
*   **用法**: `python main.py list`

### `add-account` - 添加账号
*   **功能**: 添加一个新的账号配置。
*   **用法**: `python main.py add-account --username <账号名称>`
*   **示例**: `python main.py add-account --username "我的小号"`

### `cookie` - 更新Cookie
*   **功能**: 从本地浏览器自动更新指定账号的Cookie。
*   **用法**: `python main.py cookie --account <账号名称> [--browser <浏览器名称>]`
*   **示例**: `python main.py cookie --account "我的大号"`

### `download` - 下载视频
*   **功能**: 下载无水印视频。
*   **用法**: `python main.py download --account <账号名称> --mode <模式> [--user_url <用户主页URL>]`
*   **参数**:
    *   `--account`: 指定使用哪个账号的Cookie进行下载。
    *   `--mode`:
        *   `post`: 下载用户主页作品。**必须**配合 `--user_url` 参数。
        *   `favorite`: 下载此账号收藏的作品。
    *   `--user_url`: 要下载的抖音用户主页链接。
*   **示例**:
    *   下载指定用户的作品:
        ```bash
        python main.py download --account "我的大号" --mode post --user_url "https://www.douyin.com/user/MS4wLjABAAAA..."
        ```
    *   下载自己收藏的视频:
        ```bash
        python main.py download --account "我的大号" --mode favorite
        ```

### `upload` - 上传视频
*   **功能**: 自动化上传视频到指定账号。
*   **用法**: `python main.py upload --account <账号名称> --video_path <视频文件路径> --title <视频标题> [--tags <标签1,标签2...>]`
*   **参数**:
    *   `--account`: 指定要上传到的账号。这将决定使用哪个浏览器会话文件夹。
    *   `--video_path`: 本地视频文件的完整路径。
    *   `--title`: 视频的标题（描述）。
    *   `--tags`: (可选) 视频的话题标签，多个标签用英文逗号 `,` 分隔。
*   **示例**:
    ```bash
    python main.py upload --account "我的大号" --video_path "/Users/LokiTina/Videos/旅行vlog.mp4" --title "这次的旅行太棒了！" --tags "旅行,风景,VLOG"
    ```

---

## 💡 最佳实践工作流

1.  **初始化**:
    *   使用 `add-account` 添加您需要管理的所有抖音账号。
    *   为每个账号执行一次 `cookie` 命令，完成Cookie的配置。

2.  **首次上传 (为每个账号执行一次)**:
    *   执行 `upload` 命令，指定一个账号。
    *   程序会打开一个浏览器窗口，终端会提示您登录。
    *   **请从容地在该浏览器中扫码登录**。程序会一直等待直到您登录成功。
    *   此次上传成功后，该账号的登录状态就被永久保存在对应的 `user_data_dir` 中了。

3.  **日常使用**:
    *   随时使用 `download` 命令下载视频。如果Cookie失效，重新执行 `cookie` 命令即可。
    *   使用 `upload` 命令并指定账号名，即可**免登录全自动发布**视频。

---

## ❓ 常见问题 (Troubleshooting)

*   **上传失败，提示选择器 (selector) 找不到？**
    *   抖音创作者平台的前端页面可能会不定期更新，导致代码中的UI元素选择器失效。这是所有UI自动化工具的通病。
    *   **解决方案**: 如果发生这种情况，需要更新 `uploader.py` 文件中对应的选择器。您可以参考我们调试过程中使用的方法，或提出Issue。

*   **Cookie获取失败？**
    *   请确保您已经在对应的浏览器中成功登录了抖音网页版。
    *   尝试在运行命令前，完全关闭对应的浏览器。
    *   检查 `browser-cookie3` 库是否为最新版本 (`uv pip install -U browser-cookie3`)。

---

## 展望未来

*   **开发图形用户界面 (GUI)** 以方便非技术用户使用。
*   增加更多下载模式（如：合集、直播回放等）。
*   增加更多发布选项（如：设置封面、@好友、选择合集等）。

---

## 协议

本项目采用 MIT 许可证。