import logging

def create_logger(level=logging.ERROR, name="console"):
    """
    Bootstrap the console logger
    :param level: int (default to ERROR)
    :param name: (str) name of the logger
    :return: logging.Logger
    """
    _log_format = logging.Formatter('%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:\n%(message)s\n')

    _handler = logging.StreamHandler()
    _handler.setFormatter(_log_format)
    _handler.setLevel(level)

    # setup logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(_handler)

    return logger

def get_logger(name):
    """
    Return an existing logger
    :param name: logger's name
    :return: logger with requested name
    """
    return logging.getLogger(name)