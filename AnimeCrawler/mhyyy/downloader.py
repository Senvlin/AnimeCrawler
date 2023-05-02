import asyncio

import aiohttp
import tqdm.asyncio

from AnimeCrawler.utils import write


class Downloader:
    session = None

    def __init__(self, urls):
        self.urls = urls

    @property
    def current_sesion(self):
        if not self.session:
            self.session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=40, verify_ssl=False)
            )
        return self.session

    async def get_ts_file(
        self,
        title: str,
        url: str,
        error_times: int = 1,
    ):
        resp = await self.current_sesion.get(
            url=url,
            headers={'User-Agent': 'Mozilla/5.0', 'Transfer-Encoding': 'chunked'},
        )
        try:
            text = await resp.content.read()
            return (text, title)
        except aiohttp.ClientPayloadError as e:  # 报错时重新下载
            if error_times == 3:
                raise Warning(f'下载{title}.ts时发生错误') from e
            print(f'下载{title}.ts时发生错误，正在重试第{error_times}次')
            return await self.get_ts_file(title, url, error_times + 1)
        except Exception as e:
            print(f'下载{title}.ts时发生{e}')
            await asyncio.sleep(0)
        finally:
            resp.close()

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def download_ts_files(self, path, episodes):
        tasks = [
            self.get_ts_file(str(index).zfill(4), url)
            for index, url in enumerate(self.urls)
        ]
        for task in tqdm.asyncio.tqdm.as_completed(tasks, desc=f"正在下载第{episodes}集视频"):
            result = await task
            text_1, title = (
                (b'error', 'error') if result is None else result
            )  # result为空时返回'error'
            await write(path, text_1, title, suffix='ts', mode='wb')
        await self.close_session()
