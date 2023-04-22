import logging


class ColorFilter(logging.Filter):
    FMTDCIT = {
        'ERROR': "\033[31m{}\033[0m",
        'INFO': "\033[0;37;40m{}\033[0m",
        'DEBUG': "\033[1m{}\033[0m",
        'WARNING': "\033[33m{}\033[0m",
        'CRITICAL': "\033[35m{}\033[0m",
    }

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def filter(self, record: logging.LogRecord) -> bool:
        message_level = self.FMTDCIT.get(record.levelname, 'Something went wrong')
        record.levelname = message_level.format(record.levelname)
        record.msg = message_level.format(record.msg)
        return True


def get_logger(name='') -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format='[\033[0;36;40m%(asctime)s.%(msecs)03d\033[0m] %(name)-7s | %(levelname)-7s | %(message)s',
        datefmt='%Y-%d-%m %I:%M:%S',
    )
    logger = logging.getLogger(name)
    logger.addFilter(ColorFilter())
    return logger
