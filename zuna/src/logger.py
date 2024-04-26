import logging

from zuna.src.config import Config


# BUG 当使用tqdm显示进度条时，打印的日志会使进度条显示错位
class Logger:
    """
    日志记录器
    """

    _cfg = Config()

    def __init__(self, name):
        log_level = self._cfg.config.get("common", "log_level")
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.console_handler = logging.StreamHandler()
        self.logger.addHandler(self.console_handler)

        # noqa: E501 日志颜色格式设置，这里没用colorama，是因为不想给整段日志加颜色，只给日志级别加颜色
        self.color_fmt = {
            "info": "\033[92m%(levelname)s\033[0m",
            "error": "\033[91m%(levelname)s\033[0m",
            "warning": "\033[93m%(levelname)s\033[0m",
            "debug": "\033[37m%(levelname)s\033[0m",
            "critical": "\033[1;31m%(levelname)s\033[0m",
            None: "%(levelname)s",
        }

    def _set_color(self, log_level):
        levelname = self.color_fmt.get(log_level)
        # BUG 当format中有%(lineno)d时，不显示调用方的行号，而是此文件的函数中，调用的方法行号 #noqa: E501
        formatter = logging.Formatter(
            f"%(asctime)s | [{levelname}] <%(name)s> | %(message)s",
        )

        self.console_handler.setFormatter(formatter)

    # 以下都是对外的接口
    def info(self, message):
        self._set_color("info")
        self.logger.info(message)

    def error(self, message):
        self._set_color("error")
        self.logger.error(message)

    def warning(self, message):
        self._set_color("warning")
        self.logger.warning(message)

    def debug(self, message):
        self._set_color("debug")
        self.logger.debug(message)

    def critical(self, message):
        self._set_color("critical")
        self.logger.critical(message)


if __name__ == "__main__":
    logger = Logger(__name__)
    print("---")
    logger.debug("This is a debug message")
    print("---")
    # logger.info("This is an info message")
    # logger.warning("This is a warning message")
    # logger.error("This is an error message")
