import unittest
from pathlib import Path

from zuna.src.videoIO import VideoIO, _video_folder_path


class TestCreateAnimeFolder(unittest.TestCase):
    def setUp(self):
        self.videoIO = VideoIO()
        self.anime_folder_path = _video_folder_path / "test"

    def test_create_anime_folder(self):
        self.videoIO.create_anime_folder()
        self.assertTrue(self.anime_folder_path.is_dir())

    def test_create_episode_folder(self):
        self.videoIO.create_anime_folder()
        episode_path = self.anime_folder_path / "episode_name"
        self.videoIO.create_episode_folder("episode_name")
        self.assertTrue(episode_path.is_dir())

    def test_create_episode_folder_existing(self):
        self.videoIO.create_anime_folder()
        episode_path = self.anime_folder_path / "episode_name"
        self.videoIO.create_episode_folder("episode_name")
        self.videoIO.create_episode_folder("episode_name")
        self.assertTrue(episode_path.is_dir())

    def test_create_anime_folder_existing(self):
        self.videoIO.create_anime_folder()
        self.videoIO.create_anime_folder()
        self.assertTrue(self.anime_folder_path.is_dir())


if __name__ == "__main__":
    unittest.main(buffer=True)
