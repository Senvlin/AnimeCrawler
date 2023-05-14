import logging

_str_to_level = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
}


class Logger:
    _level = 'ERROR'

    @property
    def level(self, level):
        return level

    @level.setter
    def level(self, level):
        if _str_to_level.get(level, None):
            print(level)
            self._level = level

    def get_logger(self, name='') -> logging.Logger:
        logging.basicConfig(
            level=self._level,
            format='[\033[0;36;40m%(asctime)s.%(msecs)03d\033[0m] %(name)-7s | %(levelname)-7s | %(filename)s - %(lineno)d: %(message)s',
            datefmt='%Y-%d-%m %I:%M:%S',
        )
        logger = logging.getLogger(name)
        return logger
