import re
import threading
from pathlib import Path

from downloader import Downloader
from ruia import Item, Spider, TextField
from utils.decode import base64_decode, unescape
from utils.file import folder_path, write


class AnimeItem(Item):
    target_item = TextField(xpath_select='//div[@class="player-box-main"]')
    profile = TextField(xpath_select='//div/script[@type="text/javascript"]')
    episodes = None
    _base_m3u8_url = None
    mixed_m3u8_url = None


class AnimeSpider(Spider):
    _base_ts_url = None
    _mixed_m3u8 = None
    concurrency = 1
    headers = {'User-Agent': 'Mozilla/5.0'}

    @classmethod
    def init(cls, anime_title: str, start_urls):
        cls.start_urls = start_urls
        video_path = Path(__file__).parent.parent / anime_title  # 在项目目录下存储
        cls.PATH = folder_path(video_path)
        return cls  # 为了链式调用返回了cls

    async def _mixed_m3u8_url_parse(self, index_m3u8_url: str, item: AnimeItem) -> None:
        resp = await self.request(index_m3u8_url).fetch()
        text = await resp.text()
        if self._mixed_m3u8 is None:
            self._mixed_m3u8 = text.split('\n')[-1]
        item.mixed_m3u8_url = item._base_m3u8_url + self._mixed_m3u8

    def _parse_mixed_m3u8(self, item: AnimeItem):
        '''解析mixed.m3u8文件，获得ts文件下载地址

        Returns:
            str：ts_url
        '''
        base_ts_file = item.mixed_m3u8_url[:-10]
        print(f'\033[0;32;40m{base_ts_file=}\033[0m')
        with open(self.PATH / f'{item.episodes}\\mixed.m3u8', 'r') as fp:
            for i in fp:
                if '#' not in i:
                    yield base_ts_file + i

    async def parse(self, response):
        print('\033[0;32;40mparse函数\033[0m')
        async for item in AnimeItem.get_items(html=await response.text()):
            profile = item.profile
            player_aaaa = eval(re.search('{.*}', profile).group())
            item.episodes = re.findall('\d+', response.url)[2]
            encoded_url = player_aaaa['url']
            index_m3u8_url = unescape(
                base64_decode(encoded_url)
            )  # 目标网站的index.m3u8文件地址做了加密
            item._base_m3u8_url = index_m3u8_url[:-10]
            await self._mixed_m3u8_url_parse(index_m3u8_url, item)

            link_next = player_aaaa.get('link_next', None)
            if link_next:
                # 当有下一页时
                link_next = link_next.replace('\\', '')
                print(f'\033[0;32;40m{link_next=}\033[0m')
                yield self.request(
                    'https://www.mhyyy.com' + link_next,
                    callback=self.parse,
                    headers=self.headers,
                )
        yield item

    async def process_item(self, item: AnimeItem):
        resp = await self.request(item.mixed_m3u8_url, headers=self.headers).fetch()
        text = await resp.text()
        episodes = item.episodes
        folder_path = self.PATH / f'{episodes}'
        print('\033[0;32;40m写入mixed.m3u8\033[0m')
        await write(folder_path, text, 'mixed', 'm3u8', 'w+')
        urls = self._parse_mixed_m3u8(item)
        await Downloader(urls).download_ts_files(folder_path, episodes)


if __name__ == '__main__':
    AnimeSpider.init('甘城光辉游乐园', ['https://www.mhyyy.com/play/25972-2-1.html']).start()
