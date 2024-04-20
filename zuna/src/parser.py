import re
from typing import Generator

import lxml.html


class M3u8Parser:
    def __init__(self, html_str) -> None:
        self._root = lxml.html.fromstring(html_str)

    @property
    def m3u8_url(self) -> str:
        player_datas = self._root.xpath(
            '//div[@class="player-box-main"]/script[1]/text()'
        )
        _m3u8_url: str = re.findall(r'"url":"(.*?)",', player_datas[0])[0]
        _m3u8_url = _m3u8_url.replace("\\", "")
        return _m3u8_url


class EpisodesParser:
    """对每一集信息的解析"""

    def __init__(self, html_str) -> None:
        self._root = lxml.html.fromstring(html_str)

    @property
    def episode_infos(self) -> Generator:
        infos = self._root.xpath(
            '//div \
            [@class="module-list sort-list tab-list play-tab-list active"] \
            /div/div/a'
        )
        yield from infos

    @property
    def episode_url_parts(self):
        for info in self.episode_infos:
            yield info.attrib["href"]

    @property
    def episode_names(self):
        for info in self.episode_infos:
            yield info.xpath("span/text()")[0]
