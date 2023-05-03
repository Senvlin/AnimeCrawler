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
        xpath_select='//div[@class="module-card-item-title"]/a[@rel="nofollow"]',
        many=True,
    )


class Searcher(BaseSpider):
    session = None
    downloader = None
    domain = 'https://www.mhyyy.com'
    # logger = get_logger('Searcher')

    @classmethod
    def init(cls, anime_title):
        cls.start_urls = [
            cls.urljoin(cls, cls.domain, f'/search.html?wd={anime_title}')
        ]
        return super().init()

    async def parse(self, response):
        async for item in SearchItem.get_items(html=await response.text()):
            yield item

    async def process_item(self, item: SearchItem):
        animes = tuple(enumerate(zip(item.title, item.url), start=1))
        # 美化输出
        partten = "{0}| {1}| {2}"
        print(partten.format('序号', align('标题', 38, 'C'), align('链接', 40, 'C')))
        print('-' * 90)
        for index, (title, url) in animes:
            print(
                partten.format(
                    align(str(index), 4), align(title, 37), self.domain + url
                )
            )
