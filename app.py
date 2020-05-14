from flask import Flask, request, send_file, jsonify, redirect, url_for, render_template
from logging import handlers, Formatter, getLogger, DEBUG
from scrape import scrape
from os import path


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
        return url[7:].capitalize()
    elif url.startswith('https://'):
        return url[8:].capitalize()
    return url


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


app = Flask(__name__)
log = _setup_log(file_size=5*1024*1024)


@app.route('/log')
def get_log():
    """ Sends the log file for debug """
    return send_file(LOG_FILE, as_attachment=True)


@app.route('/error')
def error():
    """ Returns static error document """
    return app.send_static_file('error.html')


@app.route('/')
def index():
    """ Returns static index document """
    return app.send_static_file('index.html')


@app.route('/', methods=['POST'])
def root():
    try:
        log.debug('Received request for {}'.format(request.form['website']))
        url = _sanitize(request.form['website'], log)
        log.debug('Received request for {}'.format(url))
        contacts = scrape(url, log)
        return render_template('results.html', website=_display(url), results=contacts)
    except Exception as e:
        log.error(e)
        return redirect(url_for('error'))


if __name__ == "__main__":
    app.run()
