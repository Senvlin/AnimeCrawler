import asyncio
from enum import Enum
from urllib.parse import urljoin

from src.item import EpisodeItem
from src.parser import EpisodesParser, M3u8Parser

from src.spider import Spider
from src.videoIO import VideoIO


class EngineState(Enum):
    init = 0
    parsing = 1
    running = 2
    done = 3


class Engine:
    def __init__(
        self,
        spider=Spider(),
        episodes_queue=asyncio.Queue(),
        video_io=VideoIO(),
    ) -> None:
        self.spider = spider
        self.episodes_queue = episodes_queue
        self.video_io = video_io
        self.state = EngineState.init

    async def init(self, root_url):
        self.video_io.create_anime_folder()
        if self.state == EngineState.init:
            # HACK 耗时多 启动慢
            html_str = await self.spider.fetch_html(root_url)
            self.state = EngineState.parsing
            print("Engine is parsing")
        episodes_parser = EpisodesParser(html_str)
        episodes, tasks = self._init_episodes(episodes_parser, root_url)
        html_strs = await asyncio.gather(*tasks)
        for episode, html_str in zip(episodes, html_strs):
            m3u8_parser = M3u8Parser(html_str)
            episode.m3u8_url = m3u8_parser.m3u8_url
            await self.episodes_queue.put(episode)

    def _init_episodes(self, episodes_parser: EpisodesParser, root_url):
        """
        HACK 我承认这里有点奇怪，但是为了重复利用代码只好这么做了

        初始化每一集

        Args:
            episodes_parser (EpisodesParser): 每一集的解析器
            root_url (str): 第一页的url

        Returns:
            tuple[list,list]: 第一个list是还没有填写m3u8_url的episode的列表
                              第二个list是返回包装每一集url的人物列表，让函数外的gather执行
                              以便获取每一集的html，然后获取m3u8_url
        """
        _tasks = []
        _episodes = []
        for episode_name, episode_url_part in zip(
            episodes_parser.episode_names,
            episodes_parser.episode_url_parts,
        ):
            episode_url = urljoin(root_url, episode_url_part)
            print(episode_url)
            _episodes.append(EpisodeItem(episode_name, episode_url))
            _tasks.append(
                asyncio.create_task(self.spider.fetch_html(episode_url))
            )
        return _episodes, _tasks

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
