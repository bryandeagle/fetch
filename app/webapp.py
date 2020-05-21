from flask import Flask, request, send_file, Response, render_template
from logging import handlers, Formatter, getLogger, INFO, DEBUG
from .scrape import scrape
from os import path
import json


AI = False
LOG_FILE = '{}.log'.format(path.basename(__file__)[0:-3])


def _sanitize(url, log):
    if not url.startswith('http'):
        new_url = 'http://{}'.format(url)
    else:
        new_url = url
    if new_url.endswith('/'):
        new_url = url[:-1]
    log.debug('URL {} sanitized to {}'.format(url, new_url))
    return new_url


def _display(url):
    if url.startswith('http://'):
        url = url[7:]
    elif url.startswith('https://'):
        url = url[8:]
    if url.startswith('www.'):
        url = url[4:]
    return url.capitalize()


def json_to_csv(json_txt, website):
    """ Convert json data to csv file """
    text = 'First Name,Last Name,Company Name,Job Title,Email ,Phone Number,Industry Role\n'
    for item in json.loads(json_txt):
        text += '{},{},{},{},{},{},\n'.format(item['first'], item['last'], website,
                                              item['position'], item['email'], item['phone'])
    return text


def _setup_log():
    """ Set up rotating log file configuration """
    log_level = DEBUG
    formatter = Formatter(fmt='[%(asctime)s] [%(levelname)s] %(message)s',
                          datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = handlers.RotatingFileHandler(filename=LOG_FILE,
                                                maxBytes=5*1024*1024,
                                                encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    logger = getLogger(__name__)
    logger.addHandler(file_handler)
    logger.setLevel(log_level)
    return logger


app = Flask(__name__, static_folder='../static')
log = _setup_log()


@app.route('/log')
def get_log():
    """ Sends the log file for debug """
    return send_file(path.join('..', LOG_FILE), as_attachment=True)


@app.route('/download', methods=['POST'])
def download():
    """ Returns CSV file """
    data = json_to_csv(request.form['data'], request.form['website'])
    return Response(data, mimetype="text/csv",
                    headers={"Content-disposition": "attachment; filename=contacts.csv"})


@app.route('/flagged', methods=['POST'])
def flagged():
    """ Returns CSV file """
    data = json_to_csv(request.form['flagged'], request.form['website'])
    return Response(data, mimetype="text/csv",
                    headers={"Content-disposition": "attachment; filename=contacts.csv"})


@app.route('/')
def index():
    """ Returns static index document """
    return app.send_static_file('index.html')


@app.route('/', methods=['POST'])
def root():
    log.info('Received request for {}'.format(request.form['website']))
    url = _sanitize(request.form['website'], log)
    try:
        contacts = scrape(website=url, log=log, ai=AI)
        if log:
            log.info('{} results found'.format(len(contacts)))
        data = json.dumps([c.dict() for c in contacts])
        flagged = json.dumps([c.dict() for c in contacts if c.hit])
        if not contacts:
            return render_template('empty.html', website=url)
        return render_template('results.html',
                               website=_display(url),
                               results=contacts,
                               data=data, flagged=flagged)
    except Exception as e:
        log.error(e)
        return render_template('error.html', website=url)
