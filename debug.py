from logging import handlers, Formatter, getLogger, DEBUG
from app import scrape
from os import path


LOG_FILE = '{}.log'.format(path.basename(__file__)[0:-3])
WEBSITE = 'http://danielcorp.com'

def _setup_log(file_size):
    """ Set up rotating log file configuration """
    formatter = Formatter(fmt='[%(asctime)s] [%(levelname)s] %(message)s',
                          datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = handlers.RotatingFileHandler(filename=LOG_FILE,
                                                maxBytes=file_size,
                                                encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(DEBUG)
    logger = getLogger(__name__)
    logger.addHandler(file_handler)
    logger.setLevel(DEBUG)
    return logger


if __name__ == '__main__':
    log = _setup_log(file_size=5 * 1024 * 1024)
    result = scrape(WEBSITE, log)
    for item in result:
        print(item)
