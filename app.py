from logging import handlers, Formatter, getLogger, DEBUG
from flask import Flask, request, send_file, jsonify
from os import path

LOG_FILE = '{}.log'.format(path.basename(__file__)[0:-3])


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


@app.route('/')
def index():
    """ Returns static index document """
    return app.send_static_file('index.html')


@app.route('/', methods=['POST'])
def root():
    return jsonify({'website': request.form['website']})


if __name__ == "__main__":
    app.run()
