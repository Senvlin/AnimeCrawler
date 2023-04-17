# README.md
<p align="center">曾几何时，打算看会动漫</p>

<p align="center">兴致勃勃，发现需要会员</p>

<p align="center">不负众望，找到免费网站</p>

<p align="center">网络原因，把我拒之门外</p>

<p align="center">惆怅万分，决定用爬虫改变现状</p>

<p align="center">离线播放，享受流畅的观看体验</p>


这是一款基于 <code>[**Ruia**](https://github.com/howie6879/ruia)</code> 轻量级框架、在Windows平台下专门爬取免费动漫的爬虫，底层使用<code>aiohttp</code>库，使用异步模式，大幅增加爬取及下载速度。可**离线播放**各大动漫，立志成为最实用，最轻量的动漫管理及下载助手

## ❓如何使用
1. 首先来到[这里](https://www.python.org/downloads)下载Python解释器, 要求Python3.8及以上版本，安装即可
    - 可能需要安装以下库：
        - ruia (<code>pip install ruia</code>)
        - tqdm (<code>pip install tqdm</code>)
        - aiohttp (<code>pip install aiohttp</code>,*注：在安装ruia的时候会自动安装*)
        - aiofiles (<code>pip install aiofiles</code>)
2. 然后点击[这里](https://github.com/Senvlin/AnimeCrawler/releases)找到最新版本，下载源码
3. 其次，来到[这个网站](https://www.mhyyy.com/),搜索您喜欢的动漫，点击播放页，将播放页的url复制一下
4. 最后，来到源码中src文件夹中的spider.py，将AnimeCrawler的init的参数修改成对应的名称及动漫，运行，就能享受到离线播放啦

如果您想体验最新的功能，请转到dev分支~

## 🚀我想帮忙
十分感谢您有这个想法。这个项目仍在青涩年华，总会有一些跌跌撞撞的时候，也许您的举手之劳，能造就更好的它。

请使用Github Issue来提交bug或功能请求。这样有利于我了解您的需求，也更好的投入精力解决问题

有的时候在dev分支中，您的需求如一些bug（或feature）已解决（或已被实现），请确认后再提交Issue

## 📝TODO

- [x] 下载多集动漫
- [x] 支持命令行工具
- [ ] 支持动漫检索
- [ ] 可更换下载源
- [ ] 支持命令行输入
- [ ] 支持上传网盘
- [ ] <span style="text-decoration: line-through">甚至是GUI</span>


## ❗ 声明
此项目只因个人兴趣而开发，仅供学习交流使用，无任何商业用途

下载的资源均来自可搜索到的、各网站提供的公开引用资源，所有视频版权均归原作者及网站所有

您应该自行承担使用此项目有可能的风险，我不保证您下载的资源的安全性，合法性，公正性。网络信息良莠不齐，请自行甄别，谢谢