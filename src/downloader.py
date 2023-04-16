import asyncio

import aiohttp
import tqdm.asyncio
from utils.file import write


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
    ) -> None:
        resp = await self.current_sesion.get(
            url=url,
            headers={'User-Agent': 'Mozilla/5.0', ' Transfer-Encoding': 'chunked'},
        )
        try:
            text = await resp.content.read()
        except aiohttp.ClientPayloadError as e:  # 报错时重新下载
            if error_times == 3:
                raise Warning(f'下载{title}.ts时发生错误') from e
            print(f'下载{title}.ts时发生错误，正在重试第{error_times}次')
            await self.get_ts_file(title, url, error_times + 1)
            await asyncio.sleep(0)
        except Exception as e:
            print(f'下载{title}.ts时发生{e}')
            await asyncio.sleep(0)
        else:
            return (text, title)
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
            text_1, title = await task
            await write(path, text_1, title, suffix='ts', mode='wb')
        await self.close_session()

    def start(self, path, episodes):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.download_ts_files(path, episodes))


if __name__ == '__main__':
    import threading
    from pathlib import Path

    thread = threading.Thread(
        target=Downloader(
            [
                'https://vip.ffzy-play2.com/20221216/12185_14bd0887/2000k/hls/4bf75419061000001.ts',
                'https://vip.ffzy-play2.com/20221216/12185_14bd0887/2000k/hls/4bf75419061000002.ts',
                'https://vip.ffzy-play2.com/20221216/12185_14bd0887/2000k/hls/4bf75419061000003.ts',
            ],
        ).start,
        args=(Path(r'C:\Users\Administrator\.python\甘城光辉游乐园'),),
    )
    thread.start()
