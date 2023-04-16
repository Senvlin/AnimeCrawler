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
    mode: str = 'a',
):
    '''在文件夹下存储文件

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
