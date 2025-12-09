# 您的作品标题

欢迎您使用本模板开始您的创作之旅！

---

**订阅我们的更新**

<!-- RSS feed link will be automatically added here -->

---

## 快速开始

### 方式一：使用模版（推荐新手）

1.  点击页面右上角的 **[Use this template](https://github.com/opensource-publish/opensource-publish/generate)** 按钮创建您的仓库。
2.  开启 **GitHub Pages** (Settings -> Pages -> Deploy from branch: main / root)。
3.  **等待发布**：修改 `config.json` 并提交后，系统会自动构建您的网站。

### 方式二：手动配置（推荐进阶用户）

如果您希望您的发布引擎永远保持最新（自动获取新功能和修复），请在您的仓库中创建文件 `.github/workflows/publish.yml` 并填入以下内容：

```yaml
name: Publish Book
on:
  push:
    paths: ['manuscripts/**.txt', 'config.json']
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: RyderFreeman4Logos/opensource-publish@main
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

这样，当本仓库更新代码（如新增打赏功能）时，您的仓库会自动享受到升级，无需手动复制代码。

---

## 使用步骤

1.  **配置**：修改 `config.json` 填写作者名和书名。
2.  **写作**：在 `manuscripts/` 目录下创建 `001 第一章.txt` 并写入内容。
3.  **打赏**：(可选) 创建 `manuscripts/donation.txt` 设置您的打赏信息。
4.  **提交**：Push 代码，系统自动构建网站。

## 关于此模板

本模板旨在帮助非技术背景的作家轻松地通过 GitHub 发布作品。它会自动处理网站生成、RSS feed 和版本控制，让您可以专注于创作。

### 核心特性

*   **零基础发布**：只需编写 TXT 文本，自动生成精美网页。
*   **阅读体验优化**：内置简约主题，支持夜间模式（取决于系统设置），提供章节导航。
*   **去中心化分发**：自动生成 RSS Feed，不再受制于单一平台的算法推荐。
*   **永久存储**：基于 Git 版本控制，您的每一个字都安全存储，历史记录可追溯。

### 许可证

*   **您的作品**：默认使用 `CC BY-NC-ND 4.0` 许可，保护您的创作权益。您可以在 `LICENSE` 文件中修改它。
*   **本模板的代码**：使用 `AGPL-3.0` 许可，确保模板本身的开源和自由。

---

如果您有任何问题或建议，欢迎[提出 issue](https://github.com/opensource-publish/opensource-publish/issues)。
