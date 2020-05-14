from flask import Flask, request, send_file, Response, render_template
from logging import handlers, Formatter, getLogger, DEBUG
from .scrape import scrape
from os import path
import json


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


app = Flask(__name__)
log = _setup_log(file_size=5*1024*1024)


@app.route('/log')
def get_log():
    """ Sends the log file for debug """
    return send_file(LOG_FILE, as_attachment=True)


@app.route('/download', methods=['POST'])
def download():
    """ Returns CSV file """
    data = json_to_csv(request.form['data'], request.form['website'])
    return Response(data, mimetype="text/csv",
                    headers={"Content-disposition": "attachment; filename=contacts.csv"})


@app.route('/')
def index():
    """ Returns static index document """
    return app.send_static_file('index.html')


@app.route('/', methods=['POST'])
def root():
    log.debug('Received request for {}'.format(request.form['website']))
    url = _sanitize(request.form['website'], log)
    try:
        contacts = scrape(url, log)
        json_txt = json.dumps([c.dict() for c in contacts])
        return render_template('results.html',
                               website=_display(url),
                               results=contacts,
                               json=json_txt)
    except Exception as e:
        log.error(e)
        return render_template('error.html', website=url)


if __name__ == "__main__":
    app.run()