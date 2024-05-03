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
        # HACK 这种parse - property的方式，局限了解析的能力，后续需要重构
        player_datas = self._root.xpath(
            '//div[@class="player-box-main"]/script[1]/text()'
        )
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


class AnimeParser:
    """
    对番剧信息的解析
    """

    def __init__(self, html_str) -> None:
        self._root = lxml.html.fromstring(html_str)

    @property
    def all_anime_infos(self):
        return self.parse()

    @property
    def has_result(self):
        return bool(tuple(self.all_anime_infos))

    def parse(self):
        """
        对外的接口，解析番剧的信息

        Returns:
            name (str): [Required] 番剧的信息，包含番剧名
            episode_state (str): [Required] 番剧的更新状态
            detail_url (str): [Required] 番剧的详情页链接
        """
        animes = self._root.xpath(
            '//div[@class="module-card-item module-item"]'
        )
        for anime in animes:
            episode_state = anime.xpath(
                'a/div/div[@class="module-item-note"]/text()'
            )[0]

            info = anime.xpath(
                'div[@class="module-card-item-info"]/ \
                               div[@class="module-card-item-title"]'
            )[0]
            name = info.xpath("a/strong/text()")[0]

            relevant_urls = anime.xpath(
                'div[@class="module-card-item-footer"]/a/@href'
            )
            # 返回解析结果时，会以(player_url, detail_url)的形式返回
            player_url, detail_url = relevant_urls[0], relevant_urls[1]
            # FIXME 返回时，必须要按照AnimeItem的属性顺序返回，否则无法正确赋值
            yield name, episode_state, player_url, detail_url
