import logging

_str_to_level = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
}


def get_logger(name='', level='DEBUG') -> logging.Logger:
    logging.basicConfig(
        level=_str_to_level[level],
        format='[\033[0;36;40m%(asctime)s.%(msecs)03d\033[0m] %(name)-7s | %(levelname)-7s | %(filename)s - %(lineno)d: %(message)s',
        datefmt='%Y-%d-%m %I:%M:%S',
    )
    logger = logging.getLogger(name)
    return logger
