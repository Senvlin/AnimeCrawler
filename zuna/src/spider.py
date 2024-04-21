import asyncio
import re
from typing import Optional
from urllib.parse import urljoin

import aiohttp
import aiohttp.client_exceptions
from zuna.src.item import EpisodeItem, M3u8, Ts
from zuna.src.settings import MAX_CONCURRENT_REQUESTS
from zuna.src.logger import Logger


class Spider:
    """负责爬取任务"""
    logger = Logger(__name__)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
    }

    def __init__(self, ts_url_queue: Optional[asyncio.Queue] = None) -> None:
        self.ts_url_queue = ts_url_queue or asyncio.Queue()
        self.session = None
        self._episode: Optional[EpisodeItem] = None

    @property
    def request_session(self) -> aiohttp.ClientSession:
        """将session包装为单例模式，防止性能开销

        Returns:
            aiohttp.ClientSession: 当时的session
        """
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    def set_episode(self, episode):
        self._episode = episode

    async def _crawler(self):
        """相当于Worker，不断爬取文件，直到队列为空"""
        while not self.ts_url_queue.empty():
            url = await self.ts_url_queue.get()
            self.logger.debug(f"Worker is processing URL: {url}")
            await self.ts_crawl(url)
            self.logger.debug(f"\033[92m Worker finished processing URL: {url}\033[0m")

    async def ts_crawl(self, url: str):
        """具体的爬取任务

        Args:
            url (str): 要爬取的url
        """
        async with self.request_session.get(url, headers=self.headers) as resp:
            ts_file = Ts(resp, self._episode.name)
            try:
                await ts_file.save()
            except aiohttp.client_exceptions.ClientPayloadError:
                self.logger.error(
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
        r = await self.fetch_html(url)
        m3u8_url_part = re.findall(r".*?.m3u8", r)[-1]
        m3u8_url = urljoin(url, m3u8_url_part)
        async with self.request_session.get(
            m3u8_url, headers=self.headers
        ) as m3u8_resp:
            m3u8 = M3u8(
                m3u8_resp, f"{self._episode.name}.m3u8", self._episode.name
            )
            await m3u8.save()
        return m3u8

    async def fetch_html(self, url):
        async with self.request_session.get(url) as response:
            html_str = await response.text()
        return html_str

    async def run(self) -> None:
        self.logger.debug("Getting m3u8...")

        m3u8 = await self.m3u8_fetch(self._episode.m3u8_url)
        ts_urls = m3u8.get_ts_urls()
        self.logger.debug("\033[92mGet m3u8 successfully\033[0m")
        async for url in ts_urls:
            await self.ts_url_queue.put(url)
        workers = []
        for _ in range(MAX_CONCURRENT_REQUESTS):
            workers.append(asyncio.create_task(self._crawler()))
        await asyncio.gather(*workers)

        await self.ts_url_queue.join()
