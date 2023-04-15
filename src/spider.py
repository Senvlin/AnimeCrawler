import asyncio
import html
import re
import urllib.parse
from base64 import b64decode
from pathlib import Path
from typing import Any, Generator

import aiofiles
import aiohttp
import tqdm.asyncio
from lxml import etree

PATH = Path(__file__).parent.parent / '甘城光辉游乐园'


class VideoParser:
    # TODO 优化m3u8下载和解析逻辑
    async def _download_m3u8(
        self, session: aiohttp.ClientSession, url: str, file_name: str = "index"
    ) -> None:
        async with session.get(url) as resp:
            m3u8_file = await resp.text()
            async with aiofiles.open(PATH / f'{file_name}.m3u8', 'w') as fp:
                await fp.write(m3u8_file)

    async def _parse_index_m3u8(self, base_url) -> str:
        '''解析index.m3u8文件，获得mixed.m3u8下载地址

        Returns:
            mixed.m3u8下载地址
        '''
        list_of_lines = list()

        async with aiofiles.open('甘城光辉游乐园/index.m3u8', 'r') as fp:
            for i in await fp.readlines():
                list_of_lines.append(i)
        mixed_m3u8_url = base_url + list_of_lines[-1]
        return mixed_m3u8_url

    def _parse_mixed_m3u8(self) -> Generator:
        '''解析index.m3u8文件，获得mixed.m3u8下载地址

        Returns:
            mixed.m3u8下载地址
        '''
        with open('甘城光辉游乐园/mixed.m3u8', 'r') as fp:
            for i in fp:
                if '#' not in i:
                    yield i

    async def parse_ts_urls(
        self, session: aiohttp.ClientSession, index_m3u8_url: str, base_url: str
    ) -> Generator[str, Any, Any]:
        print('正在解析ts文件的url')
        await self._download_m3u8(session, index_m3u8_url)
        mixed_m3u8_url = await self._parse_index_m3u8(base_url)
        await self._download_m3u8(session, mixed_m3u8_url, file_name='mixed')
        return self._parse_mixed_m3u8()


class VideoCrawler:
    async def _save_ts(self, ts_file, ts_file_name: str | int) -> None:
        '''保存ts文件

        Arguments:
            ts_file -- ts文件
            count -- 文件名
        '''
        async with aiofiles.open(PATH / f'{ts_file_name}.ts', 'wb') as fp:
            await fp.write(ts_file)

    async def ts_turn_to_mp4(self) -> None:
        print('正在转码成MP4格式')
        files = [path for path in PATH.iterdir() if path.suffix == '.ts']
        for file_path in files:
            with open(file_path, 'rb') as f1:
                with open(PATH / "甘城光辉游乐园.mp4", 'ab') as f2:
                    f2.write(f1.read())
        print('转码成功')

    async def get_ts_file(
        self,
        session: aiohttp.ClientSession,
        url: str,
        error_times: int = 1,
    ) -> None:
        ts_file_name = url[-8:-4]  # 文件名
        async with session.get(url=url) as resp:
            try:
                ts_file = await resp.content.read()
            except aiohttp.ClientPayloadError as e:  # 报错时重新下载
                if error_times == 3:
                    raise Warning(f'下载{ts_file_name}.ts时发生错误') from e
                print(f'下载{ts_file_name}.ts时发生错误，正在重试第{error_times}次')
                await self.get_ts_file(session, url, error_times + 1)
                return
            await self._save_ts(ts_file, ts_file_name)


def base64_decode(string: str) -> str:
    '''对base64.b64decode()的包装

    Arguments:
        string -- 要解码的字符串

    Returns:
        解码后的字符串
    '''
    byte = bytes(string, 'utf-8')
    string = b64decode(byte).decode()
    return string


def unescape(string) -> str:
    '''对html.unescape()的包装

    Arguments:
        string -- 要解码的字符串

    Returns:
        解码后的字符串
    '''
    string = urllib.parse.unquote(string)
    quoted = html.unescape(string).encode().decode('utf-8')
    # 转成中文
    return re.sub(
        r'%u([a-fA-F0-9]{4}|[a-fA-F0-9]{2})', lambda m: chr(int(m.group(1), 16)), quoted
    )


class HTMLParser:
    async def _get_profile(self, session: aiohttp.ClientSession, url: str) -> dict:
        async with session.get(url=url, headers={'User-Agent': 'Mozilla/5.0'}) as resp:
            html = await resp.text()
        tree = etree.HTML(html)  # type: ignore
        script: str = tree.xpath('//div/script[@type="text/javascript"]')[0].text
        player_aaaa = eval(re.search('{.*}', script).group())  # type: ignore
        print(player_aaaa)
        return player_aaaa

    async def get_index_m3u8_url(self, session: aiohttp.ClientSession, url: str) -> str:
        print('正在解析index.m3u8文件的url')
        profile = await self._get_profile(session, url)
        decoded_url = profile['url']
        print('解析完成')
        return unescape(base64_decode(decoded_url))


if __name__ == '__main__':

    async def main1() -> None:
        html_parser = HTMLParser()
        video_parser = VideoParser()
        crawler = VideoCrawler()
        tasks = []
        async with aiohttp.ClientSession() as session:
            url = await html_parser.get_index_m3u8_url(
                session, 'https://www.mhyyy.com/play/25972-2-2.html'
            )
            base_url = url[:-10]
            for url in await video_parser.parse_ts_urls(session, url, base_url):
                tasks.append(
                    crawler.get_ts_file(
                        session=session,
                        url=base_url + f'2000k/hls/{url}',
                    )
                )
            for task in tqdm.asyncio.tqdm.as_completed(tasks, desc="正在下载ts格式视频"):
                await task
        await crawler.ts_turn_to_mp4()

    asyncio.run(main1())
