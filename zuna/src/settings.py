import ctypes.wintypes
import pathlib


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
# TODO 以后改成从配置文件中读取
ANIME_NAME = "鬼灭之刃"
ANIME_FOLDER_PATH = _video_folder_path / ANIME_NAME
MAX_CONCURRENT_REQUESTS = 16 # 最大并发请求数 创建的worker不超过此数量 建议 <= 16
