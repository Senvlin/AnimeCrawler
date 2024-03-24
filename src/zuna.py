import asyncio
import pathlib
from typing import AsyncGenerator, Optional
import aiofiles
import aiohttp
from urllib.parse import urljoin
import ctypes.wintypes
import re


def get_video_path():
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, 14, None, 0, buf)
    return buf.value


VIDEO_FOLDER_PATH = pathlib.Path(get_video_path())
# TODO 以后改成从配置文件中读取
ANIME_NAME = "三体"


class M3u8:
    def __init__(
        self, response: aiohttp.ClientResponse, file_path: Optional[str] = "ceshi.m3u8"
    ):
        self.response = response
        self.url = str(response.url)
        if not file_path.endswith(".m3u8"):
            raise Exception("文件后缀应为.m3u8")
        # HACK 改一下保存逻辑
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


class Ts:
    def __init__(self, response: aiohttp.ClientResponse):
        self.response = response
        self.name = response.url.parts[-1]

    async def save(self):
        text = await self.response.content.read()
        # HACK 改一下保存逻辑
        async with aiofiles.open(
            VIDEO_FOLDER_PATH / ANIME_NAME / self.name, "wb"
        ) as fp:
            await fp.write(text)

    def __repr__(self) -> str:
        return f"<TsFile Name={self.name}>"


class Spider:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
    }

    def __init__(self, ts_url_queue: asyncio.Queue = None) -> None:
        self.ts_url_queue = ts_url_queue or asyncio.Queue()
        self.session = None
        self.file_path = ...

    @property
    def request_session(self) -> aiohttp.ClientSession:
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def crawler(self):
        while not self.ts_url_queue.empty():
            url = await self.ts_url_queue.get()
            print(f"Worker is processing URL: {url}")
            await self.ts_crawl(url)
            print(f"\033[92m Worker finished processing URL: {url}\033[0m")

    # async def _test_ts_crawl(self, url):
    #     await asyncio.sleep(2)
    #     self.ts_url_queue.task_done()

    async def ts_crawl(self, url):
        async with self.request_session.get(url, headers=self.headers) as resp:
            ts_file = Ts(resp)
            self.ts_url_queue.task_done()
            await ts_file.save()

    async def m3u8_fetch(self, url) -> M3u8:
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
            workers.append(asyncio.create_task(self.crawler()))
        await asyncio.gather(*workers)

        await self.ts_url_queue.join()
        await self.request_session.close()

    async def merge_ts(self):
        cwd = VIDEO_FOLDER_PATH / ANIME_NAME
        print(cwd)
        ts_file_paths = (path for path in cwd.iterdir() if path.suffix == ".ts")
        async with aiofiles.open(cwd / ".mp4", "wb") as parent_fp:
            for path in ts_file_paths:
                async with aiofiles.open(path, "rb") as fp:
                    text = await fp.read()
                    await parent_fp.write(text)


async def main(url):
    spider = Spider()
    await spider.run(url)
    # await spider.merge_ts()


if __name__ == "__main__":
    asyncio.run(main("https://vip.kuaikan-play2.com/20230824/IRyqtRYD/index.m3u8"))
