import unittest
from pathlib import Path
from unittest.mock import MagicMock

from aiohttp import ClientResponse

from zuna.src.item import M3u8
from zuna.src.videoIO import VideoIO


class TestM3u8(unittest.TestCase):
    def setUp(self):
        video_io = VideoIO()
        video_io.create_anime_folder()
        self.anime_folder_path = video_io.anime_folder_path
        self.response = MagicMock(spec=ClientResponse)
        self.response.url = "http://example.com/test.m3u8"
        self.child_path = Path("test")

    def test_init(self):
        # 正常情况
        m3u8 = M3u8(self.response, "test.m3u8", self.child_path)
        print(f"{m3u8.file_path=}, {self.child_path=}")
        self.assertEqual(m3u8.url, "http://example.com/test.m3u8")
        self.assertEqual(
            m3u8.file_path,
            self.anime_folder_path / self.child_path / "test.m3u8",
        )

    def test_init_without_child_path(self):
        m3u8 = M3u8(self.response, file_name="test.m3u8")
        self.assertEqual(m3u8.file_path, self.anime_folder_path / "test.m3u8")

    def test_init_file_suffix(self):
        suffixes = ["txt", "mp4", "mkv", "zip"]
        for i in suffixes:
            with self.assertRaises(Exception):
                M3u8(self.response, f"test.{i}", self.child_path)
        M3u8(self.response, "test.m3u8", self.child_path)

    def test_init_file_name_type(self):
        with self.assertRaises(Exception):
            M3u8(self.response, 123, self.child_path)

    def test_init_response_type(self):
        with self.assertRaises(Exception):
            M3u8(123, "test.m3u8", self.child_path)

    def tearDown(self):
        self.anime_folder_path.rmdir()


()

if __name__ == "__main__":
    unittest.main(buffer=True)
