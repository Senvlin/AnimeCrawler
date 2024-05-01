import asyncio
import re
from functools import wraps
from typing import Optional
from urllib.parse import urljoin

import aiohttp
import aiohttp.client_exceptions
from tqdm import tqdm

from zuna.src.config import Config
from zuna.src.item import EpisodeItem, M3u8, Ts
from zuna.src.logger import Logger


def retry(_logger: Logger, tries=4, delay=1):
    """
    一个用于异步函数的重试装饰器

    Args:
        _logger (logger): 日志记录器
        tries (int, optional): 最大重试次数. 默认为4次.
        delay (int, optional): 延迟. 默认为1秒.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            _tries, _delay = tries, delay
            while _tries > 1:
                try:
                    return await func(*args, **kwargs)
                # 给Spider.ts_crawl()做适配
                except aiohttp.client_exceptions.ClientPayloadError as e:
                    _logger.error(
                        "\033[91m The request has no content length, retry it\033[0m"  # noqa: E501
                    )

                except Exception as e:
                    _logger.error(f"\033[91m 报错了, {e}\033[0m")
                    await asyncio.sleep(_delay)
                    _tries -= 1

        return wrapper

    return decorator


class Spider:
    """负责爬取任务"""

    a = Config()
    logger = Logger(__name__)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
    }

    def __init__(self, ts_url_queue: Optional[asyncio.Queue] = None) -> None:
        self.max_concurrent_requests = self.a.config.getint(
            "download", "MAX_CONCURRENT_REQUESTS"
        )
        self.ts_url_queue = ts_url_queue or asyncio.Queue()
        self.session = None
        self._episode: Optional[EpisodeItem] = None
        self._pbar: Optional[tqdm] = None

    @property
    def request_session(self) -> aiohttp.ClientSession:
        """将session包装为单例模式，防止性能开销

        Returns:
            aiohttp.ClientSession: 当时的session
        """
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """
        关闭session
        """
        if self.session is not None:
            await self.session.close()

    async def _crawler(self):
        """相当于Worker，不断爬取文件，直到队列为空"""

        def pbar_decorator(func):
            """
            tqdm的装饰器，用于显示进度条
            # HACK 能否单独抽出来一个装饰器，不在函数中定义
            """

            @wraps(func)
            async def wrapper(*args, **kwargs):
                if self._pbar is None:
                    self._pbar = tqdm(
                        total=self.ts_url_queue.qsize(),
                        desc=f"正在下载{self._episode.name}",
                        unit="ts_it",
                    )
                result = await func(*args, **kwargs)
                # noqa: E501 这里使用if...else，是为了等待队列中的任务全部完成后，才关闭进度条
                if self._pbar.n < self._pbar.total:
                    self._pbar.update()
                else:
                    self._pbar.close()
                    # 为了下一集爬取显示进度条，这里需要重置为None
                    self._pbar = None
                return result

            return wrapper

        while not self.ts_url_queue.empty():
            url = await self.ts_url_queue.get()
            self.logger.debug(f"Worker is processing URL: {url}")
            await pbar_decorator(self.ts_crawl)(url)
            self.logger.debug(
                f"\033[92m Worker finished processing URL: {url}\033[0m"
            )
            self.ts_url_queue.task_done()

    @retry(Logger("crawler"))
    async def ts_crawl(self, url: str):
        """具体的爬取任务

        Args:
            url (str): 要爬取的url
        """
        async with self.request_session.get(url, headers=self.headers) as resp:
            ts_file = Ts(resp,self._episode.name)
            await ts_file.save()

    async def _m3u8_fetch(self, url) -> M3u8:
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
        async with self.request_session.get(url,headers=self.headers) as response:
            html_str = await response.text()
        return html_str

    async def run(self, episode) -> None:
        self._episode: EpisodeItem = episode
        self.logger.debug("Getting m3u8...")

        m3u8 = await self._m3u8_fetch(self._episode.m3u8_url)
        ts_urls = m3u8.get_ts_urls()
        self.logger.debug("\033[92mGet m3u8 successfully\033[0m")

        async for url in ts_urls:
            await self.ts_url_queue.put(url)
        workers = []
        for _ in range(self.max_concurrent_requests):
            workers.append(asyncio.create_task(self._crawler()))

        await asyncio.gather(*workers)
        await self.ts_url_queue.join()
