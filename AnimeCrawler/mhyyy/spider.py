import re
from pathlib import Path

from ruia import Item, Response, Spider, TextField

from AnimeCrawler.utils import (
    base64_decode,
    folder_path,
    get_video_path,
    merge_ts2mp4,
    unescape,
    write,
)

from .downloader import Downloader


class AnimeItem(Item):
    target_item = TextField(xpath_select='//div[@class="player-box-main"]')
    profile = TextField(xpath_select='//div/script[@type="text/javascript"]')
    episodes = None
    _base_m3u8_url = None
    mixed_m3u8_url = None


class AnimeSpider(Spider):
    _base_ts_url = None
    _mixed_m3u8 = None
    headers = {'User-Agent': 'Mozilla/5.0'}

    @classmethod
    def init(cls, anime_title: str, start_urls: str, del_ts: bool = False):
        '''初始化爬虫

        Args:
            anime_title (str): 动漫标题，用于取文件夹的名称，利于管理动漫
            start_urls (str): 第一页的网址

        Returns:
            cls: 为了链式调用返回了cls
        '''
        cls.start_urls = [start_urls]
        cls.del_ts = del_ts
        video_path = Path(get_video_path()) / anime_title  # 在项目目录下存储
        cls.PATH = folder_path(video_path)
        return cls

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
        with open(self.PATH / f'{item.episodes}\\mixed.m3u8', 'r') as fp:
            for i in fp:
                if '#' not in i:
                    yield base_ts_file + i

    async def have_next_page(self, link_next: str):
        # 当有下一页时
        link_next = link_next.replace('\\', '')
        return self.request(
            'https://www.mhyyy.com' + link_next,
            callback=self.parse,
            headers=self.headers,
        )

    async def parse(self, response: Response):
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
                yield await self.have_next_page(link_next)
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
        self.logger.info(f"正在把第 {episodes} 集的ts文件转码成 mp4")
        await merge_ts2mp4(folder_path, episodes, self.del_ts)


if __name__ == '__main__':
    AnimeSpider.init('魔女之旅', ['https://www.mhyyy.com/play/166269-1-1.html']).start()
