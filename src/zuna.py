import asyncio
import ctypes.wintypes
import pathlib
import re
from dataclasses import dataclass
from enum import Enum
from typing import AsyncGenerator, Generator, Optional
from urllib.parse import urljoin

import aiofiles
import aiohttp
import aiohttp.client_exceptions
import lxml.html


def get_video_path():
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, 14, None, 0, buf)
    return buf.value


VIDEO_FOLDER_PATH = pathlib.Path(get_video_path())
# TODO 以后改成从配置文件中读取
ANIME_NAME = "三体"


class Parser:
    def __init__(self, html_str) -> None:
        self._root = lxml.html.fromstring(html_str)


class M3u8Parser(Parser):
    def __init__(self, html_str) -> None:
        super(__class__, self).__init__(html_str)

    @property
    def m3u8_url(self) -> str:
        player_datas = self._root.xpath(
            '//div[@class="player-box-main"]/script[1]/text()'
        )
        _m3u8_url: str = re.findall(r'"url":"(.*?)",', player_datas[0])[0]
        _m3u8_url = _m3u8_url.replace("\\", "")
        return _m3u8_url


class EpisodesParser(Parser):
    """对每一集信息的解析"""

    def __init__(self, html_str) -> None:
        super(__class__, self).__init__(html_str)

    @property
    def episode_infos(self) -> Generator:
        infos = self._root.xpath(
            '//div \
            [@class="module-list sort-list tab-list play-tab-list active"] \
            /div/div/a'
        )
        yield from infos

    @property
    def episode_url_parts(self):
        for info in self.episode_infos:
            yield info.attrib["href"]

    @property
    def episode_names(self):
        for info in self.episode_infos:
            yield info.xpath("span/text()")


class M3u8:
    """对m3u8文件的包装"""

    def __init__(
        self,
        response: aiohttp.ClientResponse,
        file_path: Optional[str | pathlib.Path] = "ceshi.m3u8",
    ):
        self.response = response
        self.url = str(response.url)
        if not file_path.endswith(".m3u8"):
            raise Exception("文件后缀应为.m3u8")
        self.file_path = VIDEO_FOLDER_PATH / ANIME_NAME / file_path

    async def save(self):
        text = await self.response.content.read()
        async with aiofiles.open(self.file_path, "wb") as fp:
            await fp.write(text)

    async def get_ts_urls(self) -> AsyncGenerator:
        async with aiofiles.open(self.file_path, "r") as fp:
            text_line = await fp.readlines()
            ts_url_parts = [
                i.split("\n")[0] for i in text_line if not i.startswith("#")
            ]
            for ts_url_part in ts_url_parts:
                url = urljoin(self.url, ts_url_part)
                yield url

    def __repr__(self) -> str:
        return f"<M3u8File path={self.file_path}>"


class Ts:
    """对ts文件的包装"""

    def __init__(self, response: aiohttp.ClientResponse):
        self.response = response
        self.name = response.url.parts[-1]

    async def save(self):
        await asyncio.sleep(0)
        text = await self.response.content.read()
        async with aiofiles.open(
            VIDEO_FOLDER_PATH / ANIME_NAME / self.name, "wb"
        ) as fp:
            await fp.write(text)

    def __repr__(self) -> str:
        return f"<TsFile Name={self.name}>"


@dataclass
class Episode:
    name: str
    episode_url: Optional[str] = None
    m3u8_url: Optional[str] = None
    m3u8_path: Optional[str | pathlib.Path] = None


class Spider:
    """主要爬取一集的m3u8文件和ts文件，并把ts文件合并为mp4文件"""

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
    }

    def __init__(self, ts_url_queue: asyncio.Queue = None) -> None:
        self.ts_url_queue = ts_url_queue or asyncio.Queue()
        self.session = None

    @property
    def request_session(self) -> aiohttp.ClientSession:
        """将session包装为单例模式，防止性能开销大

        Returns:
            aiohttp.ClientSession: 当时的session
        """
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _crawler(self):
        """相当于Worker，不断爬取文件，直到队列为空"""
        while not self.ts_url_queue.empty():
            url = await self.ts_url_queue.get()
            print(f"Worker is processing URL: {url}")
            await self.ts_crawl(url)
            print(f"\033[92m Worker finished processing URL: {url}\033[0m")

    # async def _test_ts_crawl(self, url):
    #     await asyncio.sleep(2)
    #     self.ts_url_queue.task_done()

    async def ts_crawl(self, url: str):
        """具体的爬取任务

        Args:
            url (str): 要爬取的url
        """
        async with self.request_session.get(url, headers=self.headers) as resp:
            ts_file = Ts(resp)
            try:
                await ts_file.save()
            except aiohttp.client_exceptions.ClientPayloadError:
                print(
                    f"\033[91m URL: [{url}] has no content length,\
                        retry it\033[0m"
                )
                await self.ts_url_queue.put(url)
            self.ts_url_queue.task_done()

    async def m3u8_fetch(self, url) -> M3u8:
        """爬取一集的m3u8文件，为之后的ts文件解析做铺垫

        Args:
            url (str): 一集的url

        Returns:
            M3u8
        """
        async with self.request_session.get(url, headers=self.headers) as resp:
            r = await resp.text()
            m3u8_url_part = re.findall(r".*?.m3u8", r)[-1]
        m3u8_url = urljoin(url, m3u8_url_part)
        async with self.request_session.get(
            m3u8_url, headers=self.headers
        ) as m3u8_resp:
            m3u8 = M3u8(m3u8_resp)
            await m3u8.save()
        return m3u8

    async def run(self, url) -> None:
        print("Getting m3u8...")
        m3u8 = await self.m3u8_fetch(url)
        ts_urls = m3u8.get_ts_urls()
        print("Get m3u8 successfully")
        async for url in ts_urls:
            await self.ts_url_queue.put(url)
        workers = []
        for _ in range(4):
            workers.append(asyncio.create_task(self._crawler()))
        await asyncio.gather(*workers)

        await self.ts_url_queue.join()

    async def fetch_html(self, url):
        async with self.request_session.get(url) as response:
            html_str = await response.text()
        return html_str

    async def merge_ts_files(self):
        """合并ts文件为mp4文件， 目录在 VIDEO_FOLDER_PATH / ANIME_NAME"""
        cwd = VIDEO_FOLDER_PATH / ANIME_NAME
        print(cwd)
        ts_file_paths = (path for path in cwd.iterdir() if path.suffix == ".ts")
        async with aiofiles.open(cwd / f"{ANIME_NAME}.mp4", "wb") as parent_fp:
            for path in ts_file_paths:
                async with aiofiles.open(path, "rb") as fp:
                    text = await fp.read()
                    await parent_fp.write(text)


class EngineState(Enum):
    init = 0
    parsing = 1
    running = 2
    done = 3


class Engine:
    def __init__(
        self,
        spider=None,
        episodes_queue=None,
    ) -> None:
        self.spider = spider or Spider()
        self.episodes_queue = episodes_queue or asyncio.Queue()
        self.state = EngineState.init

    async def init(self, root_url):
        # TODO 初始化时创建文件夹
        if self.state == EngineState.init:
            html_str = await self.spider.fetch_html(root_url)
            self.state = EngineState.parsing
            print("Engine is parsing")
        episodes_parser = EpisodesParser(html_str)
        episodes,tasks = self._init_episodes(episodes_parser,root_url)
        html_strs = await asyncio.gather(*tasks)
        for episode,html_str in zip(episodes,html_strs):
            m3u8_parser = M3u8Parser(html_str)
            episode.m3u8_url = m3u8_parser.m3u8_url
            await self.episodes_queue.put(episode)


    def _init_episodes(self, episodes_parser: EpisodesParser, root_url):
        """
        # HACK 我承认这里有点奇怪，但是为了重复利用代码只好这么做了

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
            _episodes.append(Episode(episode_name, episode_url))
            _tasks.append(asyncio.create_task(self.spider.fetch_html(episode_url)))
        return _episodes, _tasks



    async def start_crawl(self):
        while not self.episodes_queue.empty():
            episode = await self.episodes_queue.get()
            print(episode)
            await self.spider.run(episode.m3u8_url)

    async def run(self, root_url):
        await self.init(root_url)
        self.state = EngineState.running
        try:
            await self.start_crawl()
        except Exception as e:
            self.state = EngineState.done
            print(
                f"\033[91m Error: [{e}] has been raised,\
                    shut down the Program\033[0m"
            )
        finally:
            await self.spider.request_session.close()


async def main(root_url):
    engine = Engine()
    await engine.run(root_url)


if __name__ == "__main__":
    asyncio.run(main("https://www.myd02.com/vodplay/139-3-1.html"))
