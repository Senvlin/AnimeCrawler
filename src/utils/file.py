from pathlib import Path
from typing import Union

import aiofiles


def folder_path(folder_path):
    '''判定文件夹是否存在，不存在就创建

    Args:
        folder_path (Path): 文件夹路径

    Returns:
        Path: 文件夹路径
    '''
    if not folder_path.exists():
        folder_path.mkdir()
    return folder_path


async def write(
    path: Union[str, Path],
    text: str,
    title: Union[str, int],
    suffix: str = 'txt',
    mode: str = 'w',
):
    '''使用aiofiles，在文件夹下存储文件

    Args:
        path (Path): 文件夹路径
        text (str): 文件内容
        title (str): 文件标题
        suffix (str, optional): 文件后缀. Defaults to 'txt'.
        mode (str, optional): 写入模式，

        详情请见
        https://docs.python.org/zh-cn/3.10/library/functions.html#open.

        Defaults to 'a'.
    '''
    folder = folder_path(path)
    async with aiofiles.open(folder / f'{title}.{suffix}', mode) as fp:
        await fp.write(text)


async def merge_ts2mp4(folder_path: Path, episodes: int = None):
    '''将ts文件合并成mp4

    Args:
        folder_path (Path): 文件夹路径，里面应有ts文件
        episodes (int): 动漫集数. Defaults to None.
    '''
    for file_path in folder_path.iterdir():
        if file_path.suffix == '.ts':
            with open(file_path, 'rb') as f1:
                with open(folder_path / f"第{episodes}集.mp4", 'ab') as f2:
                    f2.write(f1.read())
