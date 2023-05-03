import aiohttp
import tqdm.asyncio

from AnimeCrawler.log import get_logger
from AnimeCrawler.log import get_logger
from AnimeCrawler.utils import write


class Downloader:
    session = None
    logger = get_logger('Downloader')

    @property
    def current_sesssion(self):
        if not self.session:
            self.session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=False)
            )
            self.logger.debug('创建了session')
        return self.session

    @property
    def set_url(self, urls):
        return urls

    @set_url.setter
    def set_url(self, urls):
        self.urls = urls

    async def close_session(self):
        await self.current_session.close()

    async def get_ts_file(
        self,
        session: aiohttp.ClientSession,
        title: str,
        url: str,
        error_times: int = 1,
    ):
        resp = await session.get(
            url=url,
            headers={'User-Agent': 'Mozilla/5.0', ' Transfer-Encoding': 'chunked'},
        )
        try:
            text = await resp.content.read()
            await asyncio.sleep(0)
            return (text, title)
        except aiohttp.ClientPayloadError:  # 报错时重新下载
            if error_times == 3:
                raise Warning(f'下载{title}.ts时发生错误') from e
            print(f'下载{title}.ts时发生错误，正在重试第{error_times}次')
            return await self.get_ts_file(session, title, url, error_times + 1)
        except Exception as e:
            raise ValueError(f'下载{title}.ts时，{e}') from e
        finally:
            resp.close()

    async def download_ts_files(self, path, episodes):
        tasks = [
            self.get_ts_file(self.current_session, str(index).zfill(4), url)
            for index, url in enumerate(self.urls)
        ]
        for task in tqdm.asyncio.tqdm.as_completed(
            tasks, desc=f"正在下载第{episodes}集视频", delay=3
        ):
            result = await task
            text_1, title = (
                (b'error', 'error') if result is None else result
            )  # result为空时返回'error'
            await write(path, text_1, title, suffix='ts', mode='wb')
