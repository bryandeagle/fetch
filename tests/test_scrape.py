from app import scrape

KNOWN_RESULTS = {'http://danielcorp.com': 25, 'https://www.artspace.org/': 32, 'http://crossdevelopment.net': 16}


def test_scrape():
    raise SystemExit(1)
    for site in KNOWN_RESULTS:
        res = scrape(site)
        print('Found {} Contacts on {}. Expected {}.'.format(len(res), site, KNOWN_RESULTS[site]))
        if len(res) != KNOWN_RESULTS[site]:
            raise SystemExit(1)


if __name__ == '__main__':
    test_scrape()
