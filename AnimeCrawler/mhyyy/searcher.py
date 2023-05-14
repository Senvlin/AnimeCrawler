import itertools
from typing import Generator

from ruia import AttrField, Item, TextField

from AnimeCrawler.base_spider import BaseSpider
from AnimeCrawler.utils import align


# from AnimeCrawler.log import get_logger
class SearchItem(Item):
    target_item = TextField(
        xpath_select='//div[@class="module-items module-card-items"]'
    )
    url = AttrField(
        attr='href',
        xpath_select='//div[@class="module-card-item-footer"]/a[@class="play-btn icon-btn"]',
        many=True,
    )
    title = TextField(
        xpath_select='//div[@class="module-card-item-title"]/a[@rel="nofollow"]/strong',
        many=True,
    )
    info = TextField(
        xpath_select='//div[@class="module-card-item-info"]/div[last()]/div["module-card-item-content"]',
        many=True,
    )


class LineItem(Item):
    target_item = TextField(xpath_select='//div[@class="swiper-wrapper"]')
    line_name = TextField(
        xpath_select='//a[@data-hash="slide{1}"]',
        many=True,
    )
    line_url = AttrField(
        attr='href',
        xpath_select='//a[@data-hash="slide{1}"]',
        many=True,
    )


class Searcher(BaseSpider):
    session = None
    downloader = None
    domain = 'https://www.mh620.com'

    @classmethod
    def init(cls, anime_title, is_debug) -> BaseSpider:
        cls.start_urls = [
            cls.urljoin(cls, cls.domain, f'/search.html?wd={anime_title}')
        ]
        return super().init(is_debug)

    async def select_anime(self, animes) -> None:
        answer = input('Which anime do you want to download? >>> ')
        if answer.isdigit():
            answer = int(answer)
            anime = animes[answer - 1][1]
            title, url = anime[0].replace(' ', '_'), self.domain + anime[1]
            html = await self.request(url=url).fetch()
            await self.select_line(title, html)

    async def select_line(self, title, html):
        async for item in LineItem.get_items(html=await html.text()):
            lines = tuple(
                enumerate(
                    zip(item.line_name, item.line_url, itertools.repeat(None)),
                    start=1,
                )
            )
            await self.pretty_print(lines)
        answer = input('Which line do you expect to download? >>> ')
        if answer.isdigit():
            answer = int(answer)
            line_info = lines[answer - 1][1]
            print(
                f'\nDownload Command:\nAnimeCrawler download -t {title} -u {self.domain + line_info[1]} --del_ts'
            )

    async def pretty_print(self, items) -> None:
        partten = "{0}| {1}| {2}"
        print(partten.format('序号', align('标题', 38, 'C'), align('简介', 26, 'C')))
        print('-' * 75)
        for index, (title, _, info) in items:
            info = '无简介' if info is None else info[:12] + '...'
            print(
                partten.format(align(str(index), 4), align(title, 37), align(info, 20))
            )

    async def parse(self, response) -> Generator[SearchItem, None, None]:
        async for item in SearchItem.get_items(html=await response.text()):
            yield item

    async def process_item(self, item: SearchItem) -> None:
        animes = tuple(enumerate(zip(item.title, item.url, item.info), start=1))
        # 美化输出
        await self.pretty_print(animes)
        await self.select_anime(animes)
