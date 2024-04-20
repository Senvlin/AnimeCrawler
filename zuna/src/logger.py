import logging
from zuna.src.settings import LOG_LEVEL


class Logger:
    """
    日志记录器
    """
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(LOG_LEVEL)
        self.console_handler = logging.StreamHandler()
        self.logger.addHandler(self.console_handler)

        self.color_fmt = {
            "info": "\033[92m%(levelname)s\033[0m",
            "error": "\033[91m%(levelname)s\033[0m",
            "warning": "\033[93m%(levelname)s\033[0m",
            "debug": "\033[37m%(levelname)s\033[0m",
            "critical":"\033[1;31m%(levelname)s\033[0m",
            None: "%(levelname)s",
        }

    def _set_color(self, log_level):
        levelname = self.color_fmt.get(log_level)
        formatter = logging.Formatter(
            f"%(asctime)s | [{levelname}] <%(name)s>:Line %(lineno)d | %(message)s",
        )

        self.console_handler.setFormatter(formatter)

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
        
logger = Logger(__name__)

if __name__ == "__main__":
    print('---')
    logger.debug("This is a debug message")
    print('---')
    # logger.info("This is an info message")
    # logger.warning("This is a warning message")
    # logger.error("This is an error message")
