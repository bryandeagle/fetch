from anytree import AnyNode, RenderTree, findall
from bs4 import BeautifulSoup
from os import path, environ
from .logger import log
import requests
import string
import json
import re


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
        self.last = None
        self.hit = False

    def get_names(self):
        split = self.name.split()
        self.first, self.last = split[0], split[-1]

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
        return {'first': self.first,
                'last': self.last,
                'name': self.name,
                'email': self.email,
                'position': self.position,
                'phone': self.phone,
                'hit': self.hit}

    def __repr__(self):
        """ Print class in a pretty form """
        result = ''
        if self.hit:
            result += '[HIT]'
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
    result = ''
    for pre, fill, node in RenderTree(root_node):
        if node.parent is None:
            result += '┬\n'
        elif node.contact is None:
            result += '{}─┐\n'.format(pre[0:-1])
        else:
            result += '{}{}\n'.format(pre, node.contact)
    return result


def analyze(element):
    """ Determines if HTML element is a name, phone number, email or position """

    positions = {'accountant', 'administrator', 'analyst', 'architect', 'assistant',
                 'associate', 'auditor', 'bookkeeper', 'broker', 'buyer', 'cco', 'cdo',
                 'ceo', 'cfo', 'chro', 'cio', 'cmo', 'coo', 'cpo', 'cto', 'chief', 'clerk',
                 'collector', 'consultant', 'controller', 'coordinator', 'copywriter',
                 'designer', 'developer', 'director', 'drafter', 'engineer', 'executive',
                 'foreman', 'founder', 'head', 'lead', 'leader', 'manager', 'master',
                 'member', 'officer', 'organizer', 'overseer', 'owner', 'partner',
                 'planner', 'president', 'producer', 'programmer', 'development',
                 'proprietor', 'receptionist', 'representative', 'researcher', 'resources',
                 'risk manager', 'salesperson', 'scientist', 'secretary', 'specialist',
                 'staff', 'strategist', 'superintendent', 'supervisor', 'support',
                 'technician', 'vice', 'worker', 'chair', 'chairman', 'fellow'}

    if element.name not in [None, 'script']:
        text = ' '.join(element.find_all(text=True, recursive=False)).strip()
        if len(text) > 1:
            split_text = text.translate(str.maketrans('', '', string.punctuation)).split()
            split_text = [x.lower() for x in split_text]
            if re.match(r'^[^@]+@[^@]+\.[^@]+$', text, flags=re.IGNORECASE):
                log.debug('Detected email in: {}'.format(text))
                return Contact(email=text.lower())
            elif len(split_text) < 10 and len(set(split_text) & positions) > 0:
                log.debug('Detected position in: {}'.format(split_text))
                return Contact(position=text.title().replace('\n', ''))
            elif re.match(r'^[A-Z][a-z\'-]+(\s[A-Z][a-z\'\.-]+)?\s[A-Z][a-z\'-]+$', text, flags=re.IGNORECASE):
                log.debug('Detected name in: {}'.format(text))
                return Contact(name=text.title())
            elif re.match(r'^(\+0?1\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$', text, flags=re.IGNORECASE):
                noparen = re.sub(r'[\(\)]', '', text)
                log.debug('Detected phone in: {}'.format(text))
                return Contact(phone=re.sub(r'[-\.]', '-', noparen))
            else:
                log.debug('Detected nothing in: {} ({})'.format(text, text))


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
            if node.parent is not None:
                if node.parent.contact is None:
                    node.parent.contact = node.contact
                    node.parent = None
                elif node.contact.is_similar(node.parent.contact):
                    node.parent.contact.merge(node.contact)
                    node.parent = None


def get_contacts(root_node):
    """ Get all the contacts from our tree """
    log.debug(render_tree(root_node))
    clean_tree(root_node)
    roll_up(root_node)
    log.debug(render_tree(root_node))
    all_nodes = findall(root_node, filter_=lambda x: x.contact and x.contact.name and x.contact.position)
    [n.contact.get_names() for n in all_nodes]
    return set([n.contact for n in all_nodes])


def worth_it(html):
    """ Search for an email or phone to determine to scrape or not """
    text = html.get_text()
    email = re.match(r'[^@]+@[^@]+\.[^@]+', text, flags=re.IGNORECASE)
    phone = re.match(r'^(\+0?1\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$', text, flags=re.IGNORECASE)
    return email or phone or True


def get_all_pages(website=None, html=None, url=None):
    """ Get all pages from a given website """
    if website:
        response = requests.get(website, headers=HEADERS)
        html = response.text
        url = response.url
    site = BeautifulSoup(ignore_robots(html), features='html.parser').find(name='body')
    all_links = site.findAll('a', attrs={'href': re.compile(r'^/|({})'.format(url))})
    log.debug('Page: {}. Links: {}'.format(url, [link.get('href') for link in all_links]))
    links = set()
    for link in all_links:
        if link.get('href').startswith('/'):
            links.add('{}{}'.format(url, link.get('href')))
        else:
            links.add(link.get('href'))
    filtered = filter_links(links)
    log.debug('{} Filtered to {}'.format(links, filtered))
    return filtered


def filter_links(links):
    """ Filter known non-contact links """
    return set([link for link in links if re.match(
        r'.*(about|team|people|staff|leader|manage|executive|contact).*', link)])


def filter_contacts(contacts):
    """ Filter known bad contacts """
    contacts_list = list([c for c in contacts if c.name])
    if 'NER' in environ:
        contacts_list = [c for c in contacts_list if is_person(c.name)]
    for email in [r'^info@', r'^support@']:
        contacts_list = [c for c in contacts_list if c.email is None or not re.match(email, c.email)]
    return set(contacts_list)


def is_person(name):
    """ Determine if a name belongs to a person """
    response = requests.get('http://{}'.format(environ['NER']), params={'query': name})
    content = json.loads(response.text)
    is_person = "PERSON" in content.keys()
    log.debug('Content: {}. Person: {}'.format(content, is_person))
    return is_person


def tag_contacts(contacts):
    """ Tag contacts of interest """
    for contact in contacts:
        if re.match('.*development.*', contact.position, flags=re.IGNORECASE):
            contact.hit = True
    return sorted(contacts, key=lambda item: item.hit, reverse=True)


def ignore_robots(html):
    """ Ignore pesky tags """
    html = html.replace('<!--googleoff: index-->', '')
    html = html.replace('<!--googleon: index-->', '')
    return html


def scrape_page(website=None, html=None):
    """ Scrape a single page """
    if website:  # Download website
        html = requests.get(website, headers=HEADERS).text
    site = BeautifulSoup(ignore_robots(html), features='html.parser').find(name='body')
    # If page has no emails, ignore
    if worth_it(site):
        log.info('Parsing page: {}'.format(website))
        # Walk webpage and create tree
        root = AnyNode(contact=None)
        walker(site, root)
        found_contacts = get_contacts(root)
        for contact in found_contacts:
            log.info('  Found: {}'.format(contact))
        return found_contacts
    return set()


def scrape(website):
    """ Main function to scrape all pages """
    # Trying some new things
    log.info('Scraping {}'.format(website))
    response = requests.get(website, headers=HEADERS)
    results = scrape_page(html=response.text)
    all_pages = get_all_pages(html=response.text, url=response.url)
    log.debug('Pages: {}'.format(all_pages))
    for page in all_pages:
        found_contacts = scrape_page(website=page)
        if found_contacts:
            results.update(found_contacts)
    log.debug('Scraping complete')
    return tag_contacts(filter_contacts(results))
