import re
from pathlib import Path

import aiofiles
import utils.decode
from ruia import Item, Spider, TextField


class AnimeItem(Item):
    target_item = TextField(xpath_select='//div[@class="player-box-main"]')
    profile = TextField(xpath_select='//div/script[@type="text/javascript"]')
    episodes = None
    _base_m3u8_url = None
    mixed_m3u8_url = None


class AnimeSpider(Spider):
    _base_ts_url = None
    _mixed_m3u8 = None
    concurrency = 100
    start_urls = ['https://www.mhyyy.com/play/25972-2-1.html']
    headers = {'User-Agent': 'Mozilla/5.0'}

    @classmethod
    def init(cls, anime_title):
        video_path = Path(__file__).parent.parent / anime_title
        cls.PATH = utils.folder_path(video_path)
        return cls  # 为了链式调用返回的cls

    async def _mixed_m3u8_url_parse(self, index_m3u8_url, item: AnimeItem) -> None:
        resp = await self.request(index_m3u8_url).fetch()
        text = await resp.text()
        if self._mixed_m3u8 is None:
            self._mixed_m3u8 = text.split('\n')[-1]
        item.mixed_m3u8_url = item._base_m3u8_url + self._mixed_m3u8

    async def _download_mixed_m3u8(self, text, item: AnimeItem) -> None:
        folder_path = self.PATH / f'{item.episodes}'
        folder = utils.folder_path(folder_path)
        async with aiofiles.open(folder / 'mixed.m3u8', 'w') as fp:
            await fp.write(text)

    def _parse_mixed_m3u8(self, item: AnimeItem):
        '''解析mixed.m3u8文件，获得ts文件下载地址

        Returns:
            ts_url
        '''
        base_ts_file = item.mixed_m3u8_url[:-10]
        with open(self.PATH / f'{item.episodes}\\mixed.m3u8', 'r') as fp:
            for i in fp:
                if '#' not in i:
                    yield base_ts_file + i

    async def parse(self, response):
        print('parse函数')
        async for item in AnimeItem.get_items(html=await response.text()):
            profile = item.profile
            player_aaaa = eval(re.search('{.*}', profile).group())
            item.episodes = re.findall('\d+', response.url)[2]
            encoded_url = player_aaaa['url']
            index_m3u8_url = utils.unescape(
                utils.base64_decode(encoded_url)
            )  # 目标网站的index.m3u8文件地址做了加密
            item._base_m3u8_url = index_m3u8_url[:-10]
            await self._mixed_m3u8_url_parse(index_m3u8_url, item)

            link_next = player_aaaa.get('link_next', None)
            if link_next:
                # 当有下一页时
                link_next = link_next.replace('\\', '')
                print(f'{link_next=}')
                yield self.request(
                    'https://www.mhyyy.com' + link_next,
                    callback=self.parse,
                    headers=self.headers,
                )
            yield item

    async def process_item(self, item: AnimeItem):
        resp = await self.request(item.mixed_m3u8_url, headers=self.headers).fetch()
        text = await resp.text()
        await self._download_mixed_m3u8(text, item)
        async for resp in self.multiple_request(
            self._parse_mixed_m3u8(item), is_gather=True, headers=self.headers
        ):
            ...  # TODO 完成ts文件下载


if __name__ == '__main__':
    AnimeSpider.init('甘城光辉游乐园').start()
