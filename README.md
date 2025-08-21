### **1. 最终版 `README.md` (完整)**
# 抖音全能助手 (Douyin All-in-One Assistant)

**✨ `uv` Powered ✨**

这是一款功能强大、稳定可靠的抖音视频管理工具，基于 Python 和 Playwright 构建，专为内容创作者和运营者设计。本项目支持多账号管理，实现了自动化的无水印视频下载和视频发布功能，并采用现代化的 `uv` 工具链进行项目管理。


## 核心功能

*   **强大的账号管理系统**
    *   命令行快速 **添加/列出** 账号配置。
    *   **一键自动获取/更新** 本地已登录浏览器的Cookie，彻底告别手动复制。
*   **无水印视频下载**
    *   支持下载指定用户的**主页所有作品**。
    *   支持下载自己账号的**所有收藏视频**。
    *   支持下载指定**合集**的全部视频。
*   **自动化视频发布**
    *   **批量上传**: 支持扫描指定目录，根据文件名自动生成标题和标签进行批量发布。
    *   **多账号上传**：为每个账号保持独立的登录会话，一次扫码，永久有效。
    *   **智能等待**：自动检测登录状态，提示用户扫码并耐心等待，确保流程顺畅。

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
git clone https://github.com/kai648846760/douyin_assistant.git
cd douyin_assistant

# 或者直接解压项目文件夹并进入
cd path/to/douyin_assistant
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

### 2. 为账号自动获取Cookie
Cookie 主要用于视频下载。请先在您的电脑浏览器（如Chrome）上登录一次抖音。
```bash
python main.py cookie --account "我的大号" --browser chrome
```

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

### `cookie` - 更新Cookie
*   **功能**: 从本地浏览器自动更新指定账号的Cookie。
*   **用法**: `python main.py cookie --account <账号名称> [--browser <浏览器名称>]`

### `download` - 下载视频
*   **功能**: 下载无水印视频。
*   **用法**: `python main.py download --account <账号名称> --mode <模式> [--url <目标URL>]`
*   **参数**:
    *   `--account`: 指定使用哪个账号的Cookie进行下载。
    *   `--mode`:
        *   `post`: 下载用户主页作品。
        *   `favorite`: 下载此账号收藏的作品。
        *   `collection`: 下载合集作品。
    *   `--url`: (可选) 当 mode 为 `post` 或 `collection` 时，**必须**提供此参数。
*   **示例**:
    *   下载指定用户的作品:
        ```bash
        python main.py download --account "我的大号" --mode post --url "https://www.douyin.com/user/MS4wLjABAAAA..."
        ```
    *   下载合集:
        ```bash
        python main.py download --account "我的大号" --mode collection --url "https://www.douyin.com/collection/7476410956663228426"
        ```
    *   下载自己收藏的视频:
        ```bash
        python main.py download --account "我的大号" --mode favorite
        ```

### `upload` - 上传单个视频
*   **功能**: 自动化上传**单个**视频到指定账号。
*   **用法**: `python main.py upload --account <账号> --video_path <路径> --title <标题> [--tags <标签>]`
*   **示例**:
    ```bash
    python main.py upload --account "我的大号" --video_path "./单个视频.mp4" --title "这是一个单独的视频" --tags "测试"
    ```

### `batch-upload` - 批量上传视频 (新功能！)
*   **功能**: 扫描指定目录下的所有视频文件，并根据**文件名**自动上传。
*   **文件名约定格式**: `视频的标题 #标签1 #标签2.mp4`
    *   第一个 `#` 号之前的内容会被作为**视频标题**。
    *   后续每个 `#` 号分隔的内容都会被作为一个**话题标签**。
*   **用法**: `python main.py batch-upload --account <账号> --dir_path <目录路径> [--tags <通用标签>]`
*   **参数**:
    *   `--account`: 指定要上传到的账号。
    *   `--dir_path`: 包含所有待上传视频的**文件夹路径**。
    *   `--tags`: (可选) 为该目录下**所有视频**都添加的通用标签。
*   **示例**:
    *   假设你在 `/Users/LokiTina/Videos/待上传` 目录下有两个视频文件:
        1.  `今天天气真好 #日常 #vlog.mp4`
        2.  `我的新代码项目 #编程 #Python.mp4`
    *   执行以下命令:
        ```bash
        python main.py batch-upload --account "我的大号" --dir_path "/Users/LokiTina/Videos/待上传" --tags "原创"
        ```
    *   **程序会自动执行以下操作**:
        1.  上传 `今天天气真好 #日常 #vlog.mp4`，标题设为 `今天天气真好`，标签设为 `['原创', '日常', 'vlog']`。
        2.  上传成功后，等待10秒。
        3.  上传 `我的新代码项目 #编程 #Python.mp4`，标题设为 `我的新代码项目`，标签设为 `['原创', '编程', 'Python']`。

---

## 💡 最佳实践工作流

1.  **初始化**:
    *   使用 `add-account` 添加您需要管理的所有抖音账号。
    *   为每个账号执行一次 `cookie` 命令，完成Cookie的配置。

2.  **首次上传 (为每个账号执行一次)**:
    *   执行 `upload` 或 `batch-upload` 命令，指定一个账号。
    *   程序会打开一个浏览器窗口，终端会提示您登录。
    *   **请从容地在该浏览器中扫码登录**。程序会一直等待直到您登录成功。
    *   此次上传成功后，该账号的登录状态就被永久保存在对应的 `user_data_dir` 中了。

3.  **日常使用**:
    *   随时使用 `download` 命令下载视频。如果Cookie失效，重新执行 `cookie` 命令即可。
    *   使用 `upload` 或 `batch-upload` 并指定账号名，即可**免登录全自动发布**视频。

---

## ❓ 常见问题 (Troubleshooting)

*   **上传失败，提示选择器 (selector) 找不到？**
    *   抖音创作者平台的前端页面可能会不定期更新，导致代码中的UI元素选择器失效。这是所有UI自动化工具的通病。
    *   **解决方案**: 如果发生这种情况，需要更新 `uploader.py` 文件中对应的选择器，或在GitHub提出Issue。

*   **Cookie获取失败？**
    *   请确保您已经在对应的浏览器中成功登录了抖音网页版。
    *   尝试在运行命令前，完全关闭对应的浏览器。
    *   检查 `browser-cookie3` 库是否为最新版本 (`uv pip install -U browser-cookie3`)。

---

## 协议

本项目采用 MIT 许可证。