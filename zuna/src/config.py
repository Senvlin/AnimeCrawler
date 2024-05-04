import atexit
import logging
from configparser import ConfigParser
from pathlib import Path


class Config:
    config = ConfigParser()
    _instance = None

    # 单例模式
    def __new__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kw)
        return cls._instance

    # 读取配置文件
    def __init__(self):
        """
        如果配置文件存在就用配置文件中的值，覆盖默认值；在这个过程中如果遇到异常就保持默认值.
        程序退出时持久化配置到配置文件.
        """
        if (
            config_file := Path(".\\config\\config.ini")
        ) and config_file.exists():
            try:
                self.config.read(config_file, encoding="utf-8")
            except Exception:
                pass
        else:
            config_file.touch()
            self._create_new_config()

        # 程序退出时保存配置到配置文件
        def sync_to_disk():
            with open(config_file, "w", encoding="utf-8") as f:
                logging.info(f"save configs to [{config_file}] ")
                self.config.write(f)

        atexit.register(sync_to_disk)

    def _create_new_config(self):
        self.config.add_section("common")
        self.config.set("common", "log_level", "INFO")
        self.config.set("common", "anime_name", "None")
        self.config.add_section("download")
        self.config.set("download", "max_concurrent_requests", "16")


if __name__ == "__main__":
    a = Config()
