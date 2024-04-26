import ctypes.wintypes
import pathlib

import aiofiles

from zuna.src.config import Config
from zuna.src.logger import Logger


def get_video_path():
    """
    获取系统中视频文件夹路径

    Returns:
        Path: 视频文件夹路径
    """
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, 14, None, 0, buf)
    return pathlib.Path(buf.value)


_video_folder_path = get_video_path()


class VideoIO:
    """对视频文件的输入输出"""

    _instance = None
    logger = Logger(__name__)
    _cfg = Config()

    # 单例模式
    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    def _create_folder(self, _folder_name_or_path: pathlib.Path | str = None):
        """
        Args:
            _folder_name_or_path (pathlib.Path | str, optional): \
                文件夹名称或路径. Defaults to None.
        """

        anime_name = self._cfg.config["common"]["anime_name"]
        self.anime_folder_path = _video_folder_path / anime_name
        """
        # HACK 这里有点投机取巧了，我慢慢讲
        起因是这样，原先以上两行代码在__init__方法中。
        当初始化代码时，Config类会直接读取配置文件，将anime_name设置为之前的名称
        即使使用命令行修改后，Config.config中的anime_name并没有更新。
        以至于创建文件夹时，仍然使用旧的名称，名称错误
        现在，在修改完anime_name后，engine类会调用此方法，所以以上两行代码可以解决这个问题
        """
        if _folder_name_or_path:
            self.anime_folder_path /= _folder_name_or_path
        if not self.anime_folder_path.is_dir():
            self.anime_folder_path.mkdir()
            self.logger.info(
                f"Folder [{self.anime_folder_path}] is created successfully."
            )
        else:
            self.logger.warning(
                f"Folder [{self.anime_folder_path}] already exists."
            )

    def create_anime_folder(self):
        self._create_folder()

    def create_episode_folder(self, episode_name: str):
        self._create_folder(episode_name)

    async def merge_ts_files(self, episode_name):
        """合并ts文件为mp4文件"""
        cwd = self.anime_folder_path / episode_name
        ts_file_paths = (path for path in cwd.iterdir() if path.suffix == ".ts")
        async with aiofiles.open(
            cwd / f"{episode_name}.mp4", "wb"
        ) as parent_fp:
            for path in ts_file_paths:
                async with aiofiles.open(path, "rb") as fp:
                    text = await fp.read()
                    await parent_fp.write(text)
        self.logger.info(
            f"Merge ts files to [{cwd / f'{episode_name}.mp4'}] successfully."
        )

    async def save_file(self, path, content):
        async with aiofiles.open(path, "wb") as fp:
            await fp.write(content)
