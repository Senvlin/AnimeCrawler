import pathlib

import aiofiles

from zuna.src.settings import ANIME_FOLDER_PATH


class VideoIO:
    """对视频文件的输入输出"""

    def _create_folder(
        self, root_path, _folder_name_or_path: pathlib.Path | str = None
    ):
        if _folder_name_or_path:
            root_path /= _folder_name_or_path
        if not root_path.is_dir():
            root_path.mkdir()
            print(f"Folder [{root_path}] is created successfully.")
        else:
            print(f"Folder [{root_path}] already exists.")

    def create_anime_folder(self):
        self._create_folder(ANIME_FOLDER_PATH)

    def create_episode_folder(self, episode_name: str):
        self._create_folder(ANIME_FOLDER_PATH, episode_name)

    async def merge_ts_files(self, episode_name):
        """合并ts文件为mp4文件"""
        cwd = ANIME_FOLDER_PATH / episode_name
        ts_file_paths = (path for path in cwd.iterdir() if path.suffix == ".ts")
        async with aiofiles.open(
            cwd / f"{episode_name}.mp4", "wb"
        ) as parent_fp:
            for path in ts_file_paths:
                async with aiofiles.open(path, "rb") as fp:
                    text = await fp.read()
                    await parent_fp.write(text)
