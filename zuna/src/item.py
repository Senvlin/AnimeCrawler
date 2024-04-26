import asyncio
import pathlib
from dataclasses import dataclass
from typing import AsyncGenerator, Optional
from urllib.parse import urljoin

import aiofiles
import aiohttp

from zuna.src.videoIO import VideoIO


class MediaItem:
    """对媒体文件的包装"""

    videoIO = VideoIO()

    def __init__(
        self,
        response: aiohttp.ClientResponse,
        _child_path,
    ):
        if not isinstance(response, aiohttp.ClientResponse):
            raise ValueError(
                f"response必须为aiohttp.ClientResponse类型,而不是f{type(response)}"
            )
        self.response = response
        if not _child_path:
            _child_path = pathlib.Path(r"")
        self.parent_path = self.videoIO.anime_folder_path / _child_path


class M3u8(MediaItem):
    """对m3u8文件的包装"""

    def __init__(
        self,
        response: aiohttp.ClientResponse,
        file_name: str,
        _child_path=None,
    ):
        super().__init__(response, _child_path)
        self.url = str(response.url)
        
        self.file_path = self.parent_path / file_name

        if file_name and not file_name.endswith(".m3u8"):
            raise ValueError("文件后缀应为.m3u8")

        if not _child_path:
            _child_path = pathlib.Path(r"")
        self.file_path = self.parent_path / file_name

    async def save(self):
        text = await self.response.content.read()
        await self.videoIO.save_file(self.file_path, text)

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


class Ts(MediaItem):
    """对ts文件的包装"""

    def __init__(self, response: aiohttp.ClientResponse, _child_path=None):
        super().__init__(response, _child_path)
        self.file_name = response.url.parts[-1]
        self.file_path = self.parent_path / self.file_name

    async def save(self):
        async with aiofiles.open(self.file_path, "wb") as fp:
            while True:
                chunk = await self.response.content.read(81920)
                await asyncio.sleep(0)
                if not chunk:
                    break
                await fp.write(chunk)

    def __repr__(self) -> str:
        return f"<TsFile Name={self.file_name}>"


@dataclass
class EpisodeItem:
    name: str
    episode_url: Optional[str] = None
    m3u8_url: Optional[str] = None
    m3u8_path: Optional[str | pathlib.Path] = None
