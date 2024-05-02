import asyncio
from dataclasses import asdict
from typing import Optional

from zuna.src.item import AnimeItem
from zuna.src.parser import AnimeParser
from zuna.src.spider import Spider


class Query:
    def __init__(self, anime_parser=AnimeParser, spider=Spider()):
        self.spider = spider
        self.anime_parser = anime_parser
        self.anime_set:Optional[set] = set()

    async def search(self, name):
        root_url = (
            f"https://shoubozhan.com/vodsearch/-------------.html?wd={name}"
        )
        root_html = await self.spider.fetch_html(root_url)
        await self.spider.close()

        parser = self.anime_parser(root_html)
        if not parser.has_result:
            self.anime_set = None
        else:
            for info in parser.all_anime_infos:
                self.anime_set.add(AnimeItem(*info))

    def pretty_print(self):
        """
        print the result of search
        下个版本就改成打印表格形式
        """
        for anime in self.anime_set:
            print(asdict(anime))


if __name__ == "__main__":
    query = Query()
    asyncio.run(query.search("naruto"))
