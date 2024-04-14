import unittest
from zuna.src.videoIO import VideoIO
from zuna.src.settings import ANIME_FOLDER_PATH


class TestCreateAnimeFolder(unittest.TestCase):
    def setUp(self):
        self.videoIO = VideoIO()

    def test_create_anime_folder(self):
        self.videoIO.create_anime_folder()
        self.assertTrue(ANIME_FOLDER_PATH.is_dir())

    def test_create_episode_folder(self):
        self.videoIO.create_anime_folder()
        episode_path = ANIME_FOLDER_PATH / "episode_name"
        self.videoIO.create_episode_folder("episode_name")
        self.assertTrue(episode_path.is_dir())

    def test_create_episode_folder_existing(self):
        self.videoIO.create_anime_folder()
        episode_path = ANIME_FOLDER_PATH / "episode_name"
        self.videoIO.create_episode_folder("episode_name")
        self.videoIO.create_episode_folder("episode_name")
        self.assertTrue(episode_path.is_dir())

    def test_create_anime_folder_existing(self):
        self.videoIO.create_anime_folder()
        self.videoIO.create_anime_folder()
        self.assertTrue(ANIME_FOLDER_PATH.is_dir())


if __name__ == "__main__":
    unittest.main()
