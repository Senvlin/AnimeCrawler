import ctypes.wintypes
from pathlib import Path
from typing import Union

import aiofiles


def align(_string, _length, _type='L') -> str:
    """
    Look at https://www.jianshu.com/p/74500b7dc278

    中英文混合字符串对齐函数

    :param _string:[str]需要对齐的字符串
    :param _length:[int]对齐长度
    :param _type:[str]对齐方式（'L'：默认，左对齐；'R'：右对齐；'C'或其他：居中对齐）
    :return:[str]输出_string的对齐结果
    """
    _str_len = len(_string) + sum(u'\u4e00' <= _char <= u'\u9fff' for _char in _string)
    _space = _length - _str_len  # 计算需要填充的空格数
    if _type == 'L':  # 根据对齐方式分配空格
        _left = 0
        _right = _space
    elif _type == 'R':
        _left = _space
        _right = 0
    else:
        _left = _space // 2
        _right = _space - _left
    return ' ' * _left + _string + ' ' * _right


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


def get_video_path(path_id=14):
    '''获取用户视频文件夹路径

    Args:
        path_id (int, optional): 用户视频文件夹路径在Windows系统中的编号，不可动. Defaults to 14.

    Returns:
        str: 用户视频文件夹路径
    '''
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, path_id, None, 0, buf)
    return buf.value


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


async def merge_ts2mp4(folder_path: Path, episodes: int = None, del_ts: bool = False):
    '''将ts文件合并成mp4

    Args:
        folder_path (Path): 文件夹路径，里面应有ts文件
        episodes (int): 动漫集数. Defaults to None.
    '''
    for file_path in folder_path.iterdir():
        if file_path.suffix == '.ts':
            async with aiofiles.open(file_path, 'rb') as f1:
                async with aiofiles.open(folder_path / f"第{episodes}集.mp4", 'ab') as f2:
                    await f2.write(await f1.read())
            if del_ts:
                file_path.unlink()
