from anytree import AnyNode, RenderTree, findall
from bs4 import BeautifulSoup
import string
import re


class Contact(object):
    def __init__(self, email=None, name=None, phone=None, position=None):
        self.email = email
        self.name = name
        self.phone = phone
        self.position = position

    def merge(self, other):
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
        for child in soup.children:
            walker(child, new_node)


def tighten(node):
    """ Remove empty nodes with single-children """
    if len(node.children) == 1 and node.contact is None and node.parent is not None:
        child = node.children[0]
        child.parent = node.parent
        node.parent = None
        tighten(child)
    for child in node.children:
        tighten(child)


def prune(node):
    if node is None:
        return
    next_node = node.parent
    if not node.children and node.contact is None:
        node.parent = None
    prune(next_node)


def collect(node, results):
    if node.contact:
        c = node.contact
    else:
        c = Contact()
    for child in node.children:
        c.merge(child.contact)

    if c.is_complete():
        if c.name in results.keys():
            results[c.name].merge(c)
        else:
            results[c.name] = c

    for child in node.children:
        collect(child, results)


if __name__ == '__main__':

    # Generate our fancy tree from the HTML
    site = BeautifulSoup(open('site.html', encoding='utf-8'),
                         features='html.parser')
    root = AnyNode(contact=None)
    walker(site.find(name='body'), root)

    # Prune tree branches with no information
    for node in findall(root, filter_=lambda x: x.contact is None and not x.children):
        prune(node)

    tighten(root)  # Remove empty nodes with only one child
    results = dict()
    collect(root, results)
    real_results = [x for x in results if results[x].is_complete()]

    for item in real_results:
        print(results[item])

