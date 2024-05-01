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
        print(player_datas)
        _origin_text: str = re.findall(r'"url":"(.*?)",', player_datas[0])
        _m3u8_url = _origin_text[0].replace("\\", "")
        return _m3u8_url

class EpisodesParser:
    """对每一集信息的解析"""

    def __init__(self, html_str) -> None:
        self._root = lxml.html.fromstring(html_str)
        
    @property
    def episode_infos(self) -> Generator:
        yield from self.parse()
        
    def parse(self):
        """
        对外的接口，解析每一集的信息

        Yields:
            Iterable[tuple[url: str, name: str]]: [Required] \
                                     每一集的信息，包含episode_url和episode_name
        """
        
        infos = self._root.xpath(
            '//div \
            [@class="module-list sort-list tab-list play-tab-list active"] \
            /div/div/a'
        )
        for info in infos:
            url = info.attrib["href"]
            name = info.xpath("span/text()")[0]
            yield url, name


