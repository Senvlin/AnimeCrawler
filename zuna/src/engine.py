import asyncio
from enum import Enum
from typing import Any, AsyncGenerator
from urllib.parse import urljoin

from zuna.src.item import EpisodeItem
from zuna.src.parser import EpisodesParser, M3u8Parser

from zuna.src.spider import Spider
from zuna.src.videoIO import VideoIO


class EngineState(Enum):
    init = 0
    parsing = 1
    running = 2
    done = 3


class EpisodeFactory:
    def __init__(
        self, root_url, episodes_parser=EpisodesParser, m3u8_parser=M3u8Parser
    ) -> None:
        self.root_url = root_url
        self.m3u8_parser = m3u8_parser
        self.episodes_parser = episodes_parser

    async def create_episodes(self, spider, html_str):
        episodes_parser = self.episodes_parser(html_str)
        m3u8_parser = self.m3u8_parser(html_str)
        episodes, tasks = self._init_episodes(
            self.root_url, spider, episodes_parser
        )
        html_strs = await asyncio.gather(*tasks)
        for episode, _html_str in zip(episodes, html_strs):
            episode: EpisodeItem
            m3u8_parser = self.m3u8_parser(_html_str)
            episode.m3u8_url = m3u8_parser.m3u8_url
            yield episode

    def _init_episodes(self, root_url, spider: Spider, episodes_parser):
        """
        HACK 我承认这里有点奇怪，但是为了重复利用代码只好这么做了

        初始化每一集

        Args:
            episodes_parser (EpisodesParser): 每一集的解析器
            root_url (str): 第一页的url

        Returns:
            tuple[list,list]: 第一个list是还没有填写m3u8_url的episode的列表
                              第二个list是返回包装每一集url的列表，让函数外的gather执行
                              以便获取每一集的html，然后获取m3u8_url
        """
        _tasks = []
        _episodes = []
        for episode_name, episode_url_part in zip(
            episodes_parser.episode_names,
            episodes_parser.episode_url_parts,
        ):
            episode_url = urljoin(root_url, episode_url_part)
            _episodes.append(EpisodeItem(episode_name, episode_url))
            _tasks.append(asyncio.create_task(spider.fetch_html(episode_url)))
        return _episodes, _tasks


class Engine:
    def __init__(
        self,
        spider=Spider(),
        episodes_queue=asyncio.Queue(),
        video_io=VideoIO(),
        episode_factory=EpisodeFactory,
        m3u8_parser=M3u8Parser,
        episodes_parser=EpisodesParser,
    ) -> None:
        self.spider = spider
        self.episodes_queue = episodes_queue
        self.video_io = video_io
        self.episode_factory = episode_factory
        self.m3u8_parser = m3u8_parser
        self.episodes_parser = episodes_parser
        self.state = EngineState.init

    # HACK 对于 _init_episodes这一方法，不应放在engine类，而应该单独抽离出一个类(比如EpisodeFactory？)
    # HACK 应把parser类放在__init__()中定义，成为类属性，而不是在方法中定义
    async def init(self, root_url):
        self.video_io.create_anime_folder()
        if self.state == EngineState.init:
            # HACK 耗时多 启动慢
            html_str = await self.spider.fetch_html(root_url)
            self.state = EngineState.parsing
            print("Engine is parsing")
            self.episode_factory = self.episode_factory(
                root_url, self.episodes_parser, self.m3u8_parser
            )
        async for episode in self.episode_factory.create_episodes(
            self.spider, html_str
        ):
            await self.episodes_queue.put(episode)

    async def start_crawl(self):
        while not self.episodes_queue.empty():
            episode: EpisodeItem = await self.episodes_queue.get()
            self.video_io.create_episode_folder(episode.name)
            self.spider.set_episode(episode)
            await self.spider.run()
            await self.video_io.merge_ts_files(episode.name)

    async def run(self, root_url):
        await self.init(root_url)
        self.state = EngineState.running
        try:
            await self.start_crawl()

        # except Exception as e:
        #     print(
        #         f"\033[91m Error: [{e}] has been raised,\
        #             shut down the Program\033[0m"
        #     )
        finally:
            await self.spider.request_session.close()
            self.state = EngineState.done
