from nltk.parse import CoreNLPParser


def is_person(name):
    """ Determine if a name belongs to a person """
    ner_tagger = CoreNLPParser(url='http://localhost:9000', tagtype='ner')
    tags = [x[1] for x in ner_tagger.tag(name.split())]
    return 'PERSON' in tags


if __name__ == '__main__':

    candidates = ['Jimi Hendrix', 'Office Chair', 'Blue Grapefruit', 'Shaniqui Jones', 'Northpoint Retail']

    for candidate in candidates:
        if is_person(candidate):
            print('{}: person'.format(candidate))
        else:
            print('{}: not a person'.format(candidate))

