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
                connector=aiohttp.TCPConnector(limit=50, verify_ssl=False)
            )
        return self.session

    async def get_ts_file(
        self,
        title: str,
        url: str,
        error_times: int = 1,
    ):
        try:
            async with self.semaphore:
                resp = await self.current_session.get(
                    url=url,
                    headers={
                        'User-Agent': 'Mozilla/5.0',
                        ' Transfer-Encoding': 'chunked',
                    },
                )
                text = await resp.content.read()
                await write(path, text, title, suffix='ts', mode='wb')
        except aiohttp.ClientPayloadError as e:  # 报错时重新下载
            if error_times == 3:
                raise ValueError(f'无法下载{title}.ts') from e
            self.logger.warning(f'下载{title}.ts时发生错误，正在重试第{error_times}次')
            return await self.get_ts_file(title, url, path, error_times + 1)
        except Exception as e:
            raise ValueError(f'下载{title}.ts时，{e}') from e
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
        await tqdm.asyncio.tqdm.gather(*tasks, desc=f"正在下载第{episodes}集视频")
        await self.close_session()
