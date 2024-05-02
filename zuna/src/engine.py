import asyncio
from enum import Enum
from urllib.parse import urljoin

from zuna.src.item import EpisodeItem
from zuna.src.logger import Logger
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
        self.episodes_list = list()
        self.logger = Logger("EpisodeFactory")

    async def create_episodes(self, spider, html_str):
        episodes_parser = self.episodes_parser(html_str)
        tasks = self._init_episodes(self.root_url, spider, episodes_parser)
        html_strs = await asyncio.gather(*tasks)
        for episode, _html_str in zip(self.episodes_list, html_strs):
            self.logger.debug("adding m3u8_url to episode")
            episode = self._add_m3u8_url(episode, _html_str)
            self.logger.debug("m3u8_url is added")
            yield episode

    def _add_m3u8_url(self, episode: EpisodeItem, _html_str):
        m3u8_parser = self.m3u8_parser(_html_str)
        episode.m3u8_url = m3u8_parser.m3u8_url
        return episode

    def _init_episodes(
        self, root_url, spider: Spider, episodes_parser: EpisodesParser
    ):
        """
        HACK 我承认这里有点奇怪，但是为了重复利用代码只好这么做了

        初始化每一集

        Args:
            episodes_parser (EpisodesParser): 每一集的解析器
            spider (Spider): 爬虫模块
            root_url (str): 第一页的url

        Returns:
            list: 返回包装每一集url请求的列表，
                让函数外的gather执行,以便获取每一集的html，然后获取m3u8_url
        """
        _tasks = []
        for url_part, name in episodes_parser.episode_infos:
            _url = urljoin(root_url, url_part)
            self.episodes_list.append(EpisodeItem(name, _url))
            _tasks.append(asyncio.create_task(spider.fetch_html(_url)))
        return _tasks


class Engine:
    def __init__(
        self,
        spider=Spider(),
        episodes_queue=asyncio.Queue(),
        video_io=VideoIO(),
        logger=Logger("Engine"),
        episode_factory=EpisodeFactory,
        m3u8_parser=M3u8Parser,
        episodes_parser=EpisodesParser,
    ) -> None:
        self.spider = spider
        self.episodes_queue = episodes_queue
        self.video_io = video_io
        self.logger = logger
        self.episode_factory = episode_factory
        self.m3u8_parser = m3u8_parser
        self.episodes_parser = episodes_parser
        self.state = EngineState.init

    async def _init_episodes_queue(self, root_url):
        self.video_io.create_anime_folder()
        if self.state == EngineState.init:
            html_str = await self.spider.fetch_html(root_url)
            self.state = EngineState.parsing
            self.logger.info("Engine is parsing")
            self.episode_factory = self.episode_factory(
                root_url, self.episodes_parser, self.m3u8_parser
            )
        self.logger.debug("filling the episodes queue")
        async for episode in self.episode_factory.create_episodes(
            self.spider, html_str
        ):
            await self.episodes_queue.put(episode)
        self.logger.debug("episodes queue is filled")

    async def _start_crawl(self):
        while not self.episodes_queue.empty():
            episode: EpisodeItem = await self.episodes_queue.get()
            self.video_io.create_episode_folder(episode.name)
            await self.spider.run(episode)
            self.logger.debug("merging ts files to mp4 file")
            await self.video_io.merge_ts_files(episode.name)

    async def run(self, root_url):
        await self._init_episodes_queue(root_url)
        self.state = EngineState.running
        try:
            await self._start_crawl()
        finally:
            await self.spider.close()
            self.state = EngineState.done
