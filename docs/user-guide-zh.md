
# 开源写作模板使用指南

欢迎使用开源写作模板！本指南将引导您完成从创建新项目到发布您的第一篇文章的整个过程。即使您没有任何技术背景，也能轻松上手。

## 目录

- [准备工作](#准备工作)
- [第一步：通过模板创建您的写作仓库](#第一步通过模板创建您的写作仓库)
- [第二步：配置您的个人信息](#第二步配置您的个人信息)
- [第三步：撰写您的第一篇文章](#第三步撰写您的第一篇文章)
- [第四步：发布您的文章](#第四步发布您的文章)
- [高级功能（可选）](#高级功能可选)
  - [使用自定义域名](#使用自定义域名)
  - [查看网站分析](#查看网站分析)

## 准备工作

在开始之前，请确保您拥有一个 [GitHub](https://github.com/) 帐号。如果您还没有，可以免费注册一个。

## 第一步：通过模板创建您的写作仓库

1.  访问 [opensource-publish](https://github.com/zola-deep-thought/opensource-publish) 模板仓库。
2.  点击页面右上角的 **Use this template** 按钮。
3.  在 **Create a new repository from opensource-publish** 页面，为您的新仓库填写一个名称和描述。
4.  选择 **Public** 以便您的读者可以访问您的文章。
5.  点击 **Create repository from template**。

恭喜！您已经成功创建了自己的写作仓库。

## 第二步：配置您的个人信息

接下来，我们需要对您的写作仓库进行一些个性化配置。

1.  进入您刚刚创建的仓库页面。
2.  找到并打开 `config.json` 文件。
3.  点击文件右上角的铅笔图标 ✏️ 以编辑文件。
4.  在 `config.json` 文件中，您可以看到以下内容：

    ```json
    {
        "author": "Your Name",
        "email": "your.email@example.com",
        "title": "My Awesome Publication",
        "description": "A brief description of your publication.",
        "repo_url": "https://github.com/your-username/your-repo-name",
        "cname": "optional.yourdomain.com"
    }
    ```

5.  请根据您的实际信息修改以下字段：
    *   `author`: 您的姓名或笔名。
    *   `email`: 您的电子邮件地址。
    *   `title`: 您的出版物的标题。
    *   `description`: 对您的出版物的简短描述。

6.  修改完成后，滚动到页面底部，点击 **Commit changes** 按钮保存您的修改。

## 第三步：撰写您的第一篇文章

现在，让我们开始撰写您的第一篇文章。

1.  进入您的仓库页面。
2.  进入 `manuscripts` 文件夹。
3.  点击 **Add file** > **Create new file**。
4.  为您的文章命名，例如 `00000001 第三章 真正的勇者.txt`。**请务必使用 `.txt` 作为文件扩展名**。
6.  撰写完成后，点击 **Commit new file** 按钮保存您的文章。

## 第四步：发布您的文章

您的文章将在您提交后自动发布。发布过程可能需要几分钟时间。

发布成功后，您可以通过以下地址访问您的网站：

您的文章列表和 RSS feed 也会自动更新。


希望这份指南能帮助您顺利开始您的开源写作之旅！如果您有任何问题，欢迎随时[提出 issue](https://github.com/opensource-publish/opensource-publish/issues)。
