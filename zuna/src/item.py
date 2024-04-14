import asyncio
import pathlib
from dataclasses import dataclass
from typing import AsyncGenerator, Optional
from urllib.parse import urljoin

import aiofiles
import aiohttp
from src.settings import ANIME_FOLDER_PATH


class M3u8:
    """对m3u8文件的包装"""

    def __init__(
        self,
        response: aiohttp.ClientResponse,
        _child_path=None,
        file_name: str = "ceshi.m3u8",
    ):
        self.response = response
        self.url = str(response.url)
        if not file_name.endswith(".m3u8"):
            raise Exception("文件后缀应为.m3u8")
        self.file_path = ANIME_FOLDER_PATH / _child_path / file_name

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

    def __init__(self, response: aiohttp.ClientResponse, _child_path):
        self.response = response
        self.file_name = response.url.parts[-1]
        self.file_path = ANIME_FOLDER_PATH / _child_path / self.file_name

    async def save(self):
        await asyncio.sleep(0)
        text = await self.response.content.read()
        async with aiofiles.open(self.file_path, "wb") as fp:
            await fp.write(text)

    def __repr__(self) -> str:
        return f"<TsFile Name={self.file_name}>"


@dataclass
class EpisodeItem:
    name: str
    episode_url: Optional[str] = None
    m3u8_url: Optional[str] = None
    m3u8_path: Optional[str | pathlib.Path] = None
