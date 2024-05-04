import asyncio
import os
from dataclasses import asdict

from src.item import AnimeItem
from src.parser import AnimeParser
from src.spider import Spider


def _align(_string, _length, _type="L") -> str:
    """
    复用了原先的代码 \n
    Look at the code of below link:
    https://github.com/Senvlin/Zuna/blob/v0.2.1/AnimeCrawler/utils/file.py

    中英文混合字符串对齐函数

    Args:
        _string (_type_): 需要对齐的字符串
        _length (_type_): 对齐长度
        _type (str, optional): 对齐方式 \n
        ('L'：默认，左对齐 'R'：右对齐 'C'或其他：居中对齐). Defaults to "L".

    Returns:
        str: 输出_string的对齐结果
    """

    _str_len = len(_string) + sum(
        "\u4e00" <= _char <= "\u9fff" for _char in _string
    )
    _space = _length - _str_len  # 计算需要填充的空格数
    if _type == "L":  # 根据对齐方式分配空格
        _left = 0
        _right = _space
    elif _type == "R":
        _left = _space
        _right = 0
    else:
        _left = _space // 2
        _right = _space - _left
    return " " * _left + _string + " " * _right


def _copy(text):
    _command = f"echo {text.strip()} | clip"
    os.system(_command)


class Query:
    def __init__(self, anime_parser=AnimeParser, spider=Spider()):
        self.spider = spider
        self.anime_parser = anime_parser
        self.anime_list: list[AnimeItem | None] = list()

    async def search(self, name):
        """
        search anime by name

        Args:
            name (str): name of anime
        """
        root_url = (
            f"https://shoubozhan.com/vodsearch/-------------.html?wd={name}"
        )
        root_html = await self.spider.fetch_html(root_url)
        await self.spider.close()

        parser = self.anime_parser(root_html)
        if parser.has_result:
            for info in parser.all_anime_infos:
                self.anime_list.append(AnimeItem(*info))

    def format_result(self):
        """
        format result to string
        """
        pattern = "{0} | {1}| {2}"
        # 由于中文字符的宽度为2，所以乘以2
        max_name_length = max(
            len(asdict(item)["name"]) * 2 for item in self.anime_list
        )
        yield pattern.format(
            _align("No.", 4),
            _align("Name", max_name_length),
            _align("Episode State", 6),
        )
        yield pattern.format("-" * 4, "-" * max_name_length, "-" * 6)
        for index, anime in enumerate(self.anime_list, start=1):
            anime: AnimeItem
            yield pattern.format(
                _align(str(index), 4),
                _align(anime.name, max_name_length),
                _align(anime.episode_state, 6),
            )

    def select_anime(self, index):
        """
        select anime by index
        """
        return self.anime_list[index - 1]

    # 生成Download命令
    def generate_download_command(self, anime: AnimeItem):
        """
        generate download command by given anime
        """
        whole_url = f"https://shoubozhan.com{anime.player_url}"
        command = (
            f"py start.py download -n {anime.name} -u {whole_url}"
        )
        _copy(command)
        return command


if __name__ == "__main__":
    query = Query()
    asyncio.run(query.search("naruto"))
