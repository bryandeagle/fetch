from anytree import AnyNode, RenderTree, findall
from bs4 import BeautifulSoup
import requests
import string
import re


class Contact(object):
    def __init__(self, email=None, name=None, phone=None, position=None):
        self.email = email
        self.name = name
        self.phone = phone
        self.position = position

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


    def is_complete(self):
        return self.name is not None and self.position is not None

    def __repr__(self):
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
    return findall(root_node, filter_=lambda x: x.contact and x.contact.name and x.contact.position)


def worth_it(html):
    """ Search for an email address to determine to scrape or not """
    return re.match(r'[^@]+@[^@]+\.[^@]+', html.get_text(), flags=re.IGNORECASE)


def scrape(website):
    # Download website
    html = requests.get(website).text
    site = BeautifulSoup(html, features='html.parser').find(name='body')

    if not worth_it(site):
        return list()

    # Walk webpage and create tree
    root = AnyNode(contact=None)
    walker(site, root)
    return get_contacts(root)


if __name__ == '__main__':
    res = scrape('http://artspace.org/staff')
    for item in res:
        print(item)
