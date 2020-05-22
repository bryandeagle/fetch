# Add parent directory
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0,os.path.dirname(currentdir))

from app import scrape


WEBSITE = 'http://www.bierbrierdevelopment.com/'


if __name__ == '__main__':
    result = scrape(website=WEBSITE)
    print('{} Results Found'.format(len(result)))
