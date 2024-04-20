import pathlib

import aiofiles

from zuna.src.settings import ANIME_NAME
from zuna.src.logger import Logger
import ctypes.wintypes


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
anime_folder_path = _video_folder_path / ANIME_NAME


class VideoIO:
    """对视频文件的输入输出"""
    logger = Logger(__name__)
    def _create_folder(
        self, root_path, _folder_name_or_path: pathlib.Path | str = None
    ):
        if _folder_name_or_path:
            root_path /= _folder_name_or_path
        if not root_path.is_dir():
            root_path.mkdir()
            self.logger.info(f"Folder [{root_path}] is created successfully.")
        else:
            self.logger.warning(f"Folder [{root_path}] already exists.")

    def create_anime_folder(self):
        self._create_folder(anime_folder_path)

    def create_episode_folder(self, episode_name: str):
        self._create_folder(anime_folder_path, episode_name)

    async def merge_ts_files(self, episode_name):
        """合并ts文件为mp4文件"""
        cwd = anime_folder_path / episode_name
        ts_file_paths = (path for path in cwd.iterdir() if path.suffix == ".ts")
        async with aiofiles.open(
            cwd / f"{episode_name}.mp4", "wb"
        ) as parent_fp:
            for path in ts_file_paths:
                async with aiofiles.open(path, "rb") as fp:
                    text = await fp.read()
                    await parent_fp.write(text)
        self.logger.info(f"Merge ts files to [{cwd / f'{episode_name}.mp4'}] successfully.")
