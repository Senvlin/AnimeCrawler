import asyncio
import ctypes.wintypes
import pathlib
import re
from typing import AsyncGenerator, Generator, Iterable, Optional
from urllib.parse import urljoin

import aiofiles
import aiohttp
from bs4 import BeautifulSoup, NavigableString, Tag


def get_video_path():
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, 14, None, 0, buf)
    return buf.value


VIDEO_FOLDER_PATH = pathlib.Path(get_video_path())
# TODO 以后改成从配置文件中读取
ANIME_NAME = "三体"


class Anime: ...


class M3u8:
    def __init__(
        self,
        response: aiohttp.ClientResponse,
        file_path: Optional[str] = "ceshi.m3u8",
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
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
        async with aiofiles.open(cwd / f"{ANIME_NAME}.mp4", "wb") as parent_fp:
            for path in ts_file_paths:
                async with aiofiles.open(path, "rb") as fp:
                    text = await fp.read()
                    await parent_fp.write(text)


class EpisodeParser:
    # DONE 完成对每一集信息的解析
    # DONE 应先获得每一集信息，再从信息中过滤出url和name

    def __init__(self, html_str) -> None:
        self.root = BeautifulSoup(html_str, 'html.parser')

    @property
    def episode_infos(self) -> Generator:
        play_tab_list = self.root.find('div', class_='module-list sort-list tab-list play-tab-list active')
        infos = play_tab_list.find_all('a', class_='module-play-list-link')
        for info in infos:
            yield info

    @property
    def episode_url_parts(self):
        for info in self.episode_infos:
            yield info.attrs['href']

    @property
    def episode_names(self):
        for info in self.episode_infos:
            yield info.text.replace('\n', '')


async def main(url):
    # spider = Spider()
    # await spider.run(url)
    # await spider.merge_ts()
    async with aiofiles.open("a.html", "r", encoding="utf-8") as fp:
        html_str = await fp.read()
    parser = EpisodeParser(html_str)
    for url in parser.episode_names:
        print(url)


if __name__ == "__main__":
    asyncio.run(
        main(
            "https://svipsvip.ffzy-online5.com/20230930/17311_4c0bc7b2/index.m3u8"
        )
    )
