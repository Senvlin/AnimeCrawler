import logging


def get_logger(name='') -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format='[\033[0;36;40m%(asctime)s.%(msecs)03d\033[0m] %(name)-7s | %(levelname)-7s | %(filename)s - %(lineno)d: %(message)s',
        datefmt='%Y-%d-%m %I:%M:%S',
    )
    logger = logging.getLogger(name)
    return logger
