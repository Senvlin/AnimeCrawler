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


class Searcher(BaseSpider):
    session = None
    downloader = None
    domain = 'https://www.mhyyy.com'
    # logger = get_logger('Searcher')

    @classmethod
    def init(cls, anime_title) -> BaseSpider:
        cls.start_urls = [
            cls.urljoin(cls, cls.domain, f'/search.html?wd={anime_title}')
        ]
        return super().init()

    async def select_anime(self, animes) -> None:
        answer = int(input('Which anime do you want to download? >>> '))
        anime = animes[answer - 1][1]
        title, url = anime[0].replace(' ', '_'), self.domain + anime[1]
        print(
            f'\nDownload Command:\nAnimeCrawler download -t {title} -u {url} --del_ts'
        )

    async def pretty_print(self, animes) -> None:
        partten = "{0}| {1}|"
        print(partten.format('序号', align('标题', 38, 'C')))
        print('-' * 45)
        for index, (title, _) in animes:
            print(partten.format(align(str(index), 4), align(title, 37)))

    async def parse(self, response) -> Generator[SearchItem, None, None]:
        async for item in SearchItem.get_items(html=await response.text()):
            yield item

    async def process_item(self, item: SearchItem) -> None:
        animes = tuple(enumerate(zip(item.title, item.url), start=1))
        # 美化输出
        await self.pretty_print(animes)
        await self.select_anime(animes)
