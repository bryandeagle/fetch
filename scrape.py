from logging import handlers, Formatter, getLogger, DEBUG
from anytree import AnyNode, RenderTree, findall
from bs4 import BeautifulSoup
from os import path
import requests
import string
import re


LOG_FILE = '{}.log'.format(path.basename(__file__)[0:-3])
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/39.0.2171.95 Safari/537.36'}


class Contact(object):
    def __init__(self, email=None, name=None, phone=None, position=None):
        self.email = email
        self.name = name
        self.phone = phone
        self.position = position
        self.first = None

    def get_first(self):
        self.first = self.name.split()[0]

    def merge(self, other):
        """ Merge contact with another contact """
        if other is None:
            return
        if self.email is None:
            self.email = other.email
        if self.name is None:
            self.name = other.name
        if self.phone is None:
            self.phone = other.phone
        if self.position is None:
            self.position = other.position

    def is_similar(self, other):
        """ Determine if two partial contacts are similar """
        name = self.name is None or other.name is None or self.name == other.name
        email = self.email is None or other.email is None or self.email == other.email
        phone = self.phone is None or other.phone is None or self.phone == other.phone
        position = self.position is None or other.position is None or self.position == other.position
        return name and email and phone and position

    def dict(self):
        """ Return class in dictionary format """
        return {'name': self.name, 'email': self.email, 'position': self.position, 'phone': self.phone}

    def __repr__(self):
        """ Print class in a pretty form """
        result = ''
        if self.name is not None:
            result += 'Name:{} '.format(self.name)
        if self.email is not None:
            result += 'Email:{} '.format(self.email)
        if self.phone is not None:
            result += 'Phone:{} '.format(self.phone)
        if self.position is not None:
            result += 'Position:{} '.format(self.position)
        return result[:-1]


def render_tree(root_node):
    """ Print tree for debugging """
    for pre, fill, node in RenderTree(root_node):
        if node.parent is None:
            print('┬')
        elif node.contact is None:
            print('{}─┐'.format(pre[0:-1]))
        else:
            print('{}{}'.format(pre, node.contact))


def analyze(element):
    """ Determines if HTML element is a name, phone number, email or position """
    positions = {'development', 'senior', 'vice', 'president', 'director', 'administrator'
                 'manager', 'strategist', 'analyst', 'associate', 'assistant', 'bookkeeper',
                 'chief', 'coo', 'cfo', 'cto', 'lead'}
    if element.name not in [None, 'script']:
        text = ' '.join(element.find_all(text=True, recursive=False)).strip()
        if len(text) > 1:
            split_text = text.translate(str.maketrans('', '', string.punctuation)).split()
            split_text = [x.lower() for x in split_text]
            if re.match(r'^[^@]+@[^@]+\.[^@]+$', text, flags=re.IGNORECASE):
                return Contact(email=text.lower())
            elif len(split_text) < 10 and len(set(split_text) & positions) > 0:
                return Contact(position=text.title())
            elif re.match(r'^[A-Z][a-z\'-]+(\s[A-Z][a-z\'-]+)?\s[A-Z][a-z\'-]+$', text, flags=re.IGNORECASE):
                return Contact(name=text.title())
            elif re.match(r'^(\+0?1\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$', text, flags=re.IGNORECASE):
                noparen = re.sub(r'[\(\)]', '', text)
                return Contact(phone=re.sub(r'[-\.]', '-', noparen))


def walker(soup, node):
    """ Traverses the bs4 tree and constructs a new one """
    if soup.name is not None:
        new_node = AnyNode(parent=node, contact=analyze(soup))
        [walker(child, new_node) for child in soup.children]


def tighten(node):
    """ Remove empty nodes with single-children """
    if len(node.children) == 1 and node.contact is None and node.parent is not None:
        child = node.children[0]
        child.parent = node.parent
        node.parent = None
        tighten(child)
    for child in node.children:
        tighten(child)


def clean_tree(root_node):
    """ Prune entire tree of empty branches """
    [prune_node(x) for x in root_node.leaves if x.contact is None]
    tighten(root_node)


def prune_node(node):
    """ Prune a given node of empty branches """
    if node is None:
        return
    next_node = node.parent
    if not node.children and node.contact is None:
        node.parent = None
    prune_node(next_node)


def roll_up(root_node):
    """ Roll up contact information """
    leaf_nodes = None
    while root_node.leaves != leaf_nodes:
        leaf_nodes = root_node.leaves
        for node in leaf_nodes:
            if node.parent.contact is None:
                node.parent.contact = node.contact
                node.parent = None
            elif node.contact.is_similar(node.parent.contact):
                node.parent.contact.merge(node.contact)
                node.parent = None


def get_contacts(root_node):
    """ Get all the contacts from our tree """
    clean_tree(root_node)
    roll_up(root_node)
    all_nodes = findall(root_node, filter_=lambda x: x.contact and x.contact.name and x.contact.position)
    [n.contact.get_first() for n in all_nodes]
    return [n.contact for n in all_nodes]


def worth_it(html):
    """ Search for an email address to determine to scrape or not """
    return re.match(r'[^@]+@[^@]+\.[^@]+', html.get_text(), flags=re.IGNORECASE)


def get_all_pages(website, base, level=0):
    """ Get all pages from a given website """
    html = requests.get(website, headers=HEADERS).text
    site = BeautifulSoup(ignore_robots(html), features='html.parser').find(name='body')
    all_links = site.findAll('a', attrs={'href': re.compile('^/')})
    if level == 1:
        return ['{}{}'.format(base, link.get('href')) for link in all_links]
    else:
        for link in all_links:
            return get_all_pages('{}{}'.format(website, link.get('href')), base=base, level=level+1)


def ignore_robots(html):
    """ Ignore pesky tags """
    html.replace('<!--googleoff: index-->', '')
    html.replace('<!--googleon: index-->', '')
    return html


def scrape(website, log):
    results = set()
    all_pages = set(get_all_pages(website, website))
    log.debug('Pages: {}'.format(all_pages))
    for page in all_pages:
        # Download website
        html = requests.get(page, headers=HEADERS).text
        site = BeautifulSoup(ignore_robots(html), features='html.parser').find(name='body')
        log.debug(html)
        # If page has no emails, ignore
        if worth_it(site):
            log.debug('Parsing page: {}'.format(page))
            # Walk webpage and create tree
            root = AnyNode(contact=None)
            walker(site, root)
            found_contacts = get_contacts(root)
            for contact in found_contacts:
                log.debug('Found: {}'.format(contact))
            results.update(found_contacts)
    log.debug('Scraping complete')
    return results


def _setup_log(file_size):
    """ Set up rotating log file configuration """
    formatter = Formatter(fmt='[%(asctime)s] [%(levelname)s] %(message)s',
                          datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = handlers.RotatingFileHandler(filename=LOG_FILE,
                                                maxBytes=file_size)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(DEBUG)
    logger = getLogger(__name__)
    logger.addHandler(file_handler)
    logger.setLevel(DEBUG)
    return logger


if __name__ == '__main__':
    log = _setup_log(file_size=5 * 1024 * 1024)
    res = scrape('https://www.ryancompanies.com', log)
    for item in res:
        print(item)
