from logging import handlers, Formatter, getLogger, DEBUG, StreamHandler
from app import scrape
from os import path


LOG_FILE = '{}.log'.format(path.basename(__file__)[0:-3])
WEBSITE = 'https://duwestrealty.com/about/'


def _setup_log():
    """ Set up rotating log file configuration """
    log_level = DEBUG
    formatter = Formatter(fmt='[%(asctime)s] [%(levelname)s] %(message)s',
                          datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = handlers.RotatingFileHandler(filename=LOG_FILE,
                                                maxBytes=5 * 1024 * 1024,
                                                encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    logger = getLogger(__name__)
    logger.addHandler(file_handler)
    stream_handler = StreamHandler()
    stream_handler.setLevel(log_level)
    logger.addHandler(stream_handler)
    logger.setLevel(log_level)
    return logger


if __name__ == '__main__':
    log = _setup_log()
    result = scrape(website=WEBSITE, log=log, ai=False)
