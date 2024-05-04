# README

## 简介

本项目是一款基于Python的动漫下载器，可以从网站下载视频，并提供搜索功能。
原名为`AnimeCrawler`[^1], 后改名为`Zuna`.

不同于初版依赖于[`ruia`](https://github.com/howie6879/ruia)框架，本版采用自己写的框架，底层使用`aiohttp`库进行异步请求，由`tqdm`库实现进度条显示，使用`click`库实现命令行交互。

> 注意：本项目仅供学习交流使用，请不要用于商业用途。下载速度取决于网络环境，下载时间取决于网站响应速度。
## 预览

![preview](https://img2.imgtp.com/2024/05/04/CKItG9ID.gif)

## 安装

### 前置工作

- 安装Python 3.10+ (修改一下Type Hint语法可以支持Python 3.9，后续看情况会扩大适配范围)

### 安装方式

1. 下载源码
    - 使用`pip install -r requirements.txt`安装依赖库
2. 在命令行中使用`cd` 切换到项目中的`zuna`目录
3. 使用`python cli.py COMMAND`启动程序
    - `COMMAND`为子命令，具体见下文。

### 子命令

- `search`：搜索功能，输入关键字搜索相关动漫，并显示搜索结果，选择编号可以生成下载命令。
- `download`：下载功能，一般用生成好的就行。
- `config`：配置功能，设置日志等级、最大并发数等。
- `--help`：显示帮助信息。


## 目前进度
- [x] 重构下载模块 (14.04.2024)
- [x] 重构cli (26.04.2024)
- [x] 重构搜索模块 (03.05.2024)
- [ ] 增加管理功能
- [ ] 支持换源下载
- [ ] 完善文档
- [ ] 将视频上传网盘
- [ ] 发布重构版本的pypi包
- [ ] ~~GUI开发~~ (暂时不打算)

[^1]: ~~源码：https://github.com/Senvlin/Zuna/tree/v0.2.1， Pypi：https://pypi.org/project/AnimeCrawler/~~ 黑历史就别看了 (✿◡‿◡)