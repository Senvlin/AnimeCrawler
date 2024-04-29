import re
from typing import Generator

import lxml.html

class M3u8Parser:
    def __init__(self, html_str) -> None:
        self._root = lxml.html.fromstring(html_str)

    @property
    def m3u8_url(self) -> str:
        return self.parse()

    def parse(self):
        player_datas = self._root.xpath(
            '//div[@class="player-box-main"]/script[1]/text()'
        )
        _m3u8_url: str = re.findall(r'"url":"(.*?)",', player_datas[0])[0].replace("\\", "")
        return _m3u8_url

class EpisodesParser:
    """对每一集信息的解析"""

    def __init__(self, html_str) -> None:
        self._root = lxml.html.fromstring(html_str)

    def parse(self):
        """
        对外的接口，解析每一集的信息

        Returns:
            Iterable: [Required] 一集的信息
        """
        # HACK episode_url_parts episode_names 都依赖于此 想要把解析逻辑分离还得再改改
        
        infos = self._root.xpath(
            '//div \
            [@class="module-list sort-list tab-list play-tab-list active"] \
            /div/div/a'
        )
        return infos

    @property
    def episode_infos(self) -> Generator:
        yield from self.parse()

    @property
    def episode_url_parts(self):
        for info in self.episode_infos:
            yield info.attrib["href"]

    @property
    def episode_names(self):
        for info in self.episode_infos:
            yield info.xpath("span/text()")[0]
