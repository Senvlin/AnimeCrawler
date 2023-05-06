# README.md
<p align="center">曾几何时，打算看会动漫</p>

<p align="center">兴致勃勃，发现需要会员</p>

<p align="center">不负众望，找到免费网站</p>

<p align="center">网络原因，把我拒之门外</p>

<p align="center">惆怅万分，决定用爬虫改变现状</p>

<p align="center">离线播放，享受流畅的观看体验</p>


这是一款在Windows平台下基于轻量级框架<code>[**Ruia**](https://github.com/howie6879/ruia)</code>、专门爬取免费动漫的爬虫，底层使用<code>aiohttp</code>库，使用异步模式，大幅增加爬取及下载速度。可**离线播放**各大动漫，支持**命令行输入**，立志成为最实用，最轻量的动漫管理及下载助手

## ❓如何使用
1. 首先来到[这里](https://www.python.org/downloads)下载Python解释器, 要求Python3.8及以上版本，安装即可
2. 然后，打开命令提示符，输入 <code>pip install AnimeCrawler</code>
3. 其次，输入 <code>AnimeCrawler search -t "动漫标题"</code>，来搜索动漫
4. 最后，复制输出的下载命令，粘贴回车就可以下载啦
    - 输入 <code>AnimeCrawler -h</code> 会有详细的说明
> 下载后的文件在您的视频文件夹里

如果您想体验最新的功能，请转到dev分支~

## 🚀我想帮忙
十分感谢您有这个想法。这个项目仍在青涩年华，总会有一些跌跌撞撞的时候，也许您的举手之劳，能造就更好的它

请使用Github Issue来提交bug或功能请求。这样有利于我了解您的需求，也更好的投入精力解决问题。力所能及的话，可以先提个Issue后拉个Pull Requests，那样再好不过了

> 有的时候在dev分支中，您的需求如一些bug（或feature）已解决（或已被实现），请确认后再提交Issue

## 📝TODO

- [x] 下载多集动漫
- [x] 支持命令行工具
- [ ] 支持检索动漫
- [ ] 可更换下载源
- [ ] 支持上传网盘
- [ ] <span style="text-decoration: line-through">甚至是GUI</span>

## 🧱从源码搭建
1. 点击[这里](https://github.com/Senvlin/AnimeCrawler/releases)找到最新版本，下载源码
2. 转到项目目录，使用 <code>pip install -r requirement.txt</code> 安装依赖库
3. 随后使用 <code>python -m AnimeCrawler download -t "动漫标题" -u "URL"</code> 运行即可

## ❗ 声明
此项目只因个人兴趣而开发，仅供学习交流使用，无任何商业用途

下载的资源均来自可搜索到的、各网站提供的公开引用资源，所有视频版权均归原作者及网站所有

您应该自行承担使用此项目有可能的风险，我不保证您下载的资源的安全性，合法性，公正性。网络信息良莠不齐，请自行甄别，谢谢