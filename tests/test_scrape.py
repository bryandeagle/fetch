from logging import getLogger, DEBUG, StreamHandler
from app import scrape_page, get_all_pages, Contact


def _setup_log():
    """ Set up stdout log configuration """
    log_level = DEBUG
    logger = getLogger(__name__)
    stream_handler = StreamHandler()
    stream_handler.setLevel(log_level)
    logger.addHandler(stream_handler)
    logger.setLevel(log_level)
    return logger


def test_links(log=None):
    """ Test ability to find links """
    html = open('tests/links.html', 'rt').read()
    x = get_all_pages(html=html, url='http://example.com', log=log)
    print(x)
    if x != {'http://example.com/contact-us'}:
        raise SystemExit(1)


def test_scrape(log=None):
    """ Test ability to scrape contacts """
    test_contact = Contact(name='John Lennon',
                           email='john.lennon@beatles.com',
                           phone='555-123-4567',
                           position='Chief Executive Officer')
    html = open('tests/contacts.html', 'rt').read()
    result = list(scrape_page(html=html, log=log))[0]
    if not result.is_similar(test_contact) or \
            not test_contact.is_similar(result):
        raise SystemExit(1)


if __name__ == '__main__':
    log = _setup_log()
    test_links()
    test_scrape(log)
