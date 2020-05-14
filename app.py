from logging import handlers, Formatter, getLogger, DEBUG
from flask import Flask, request, send_file, Response, send_from_directory
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from pypandoc import convert_text
from time import time, localtime
from io import BytesIO
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
    return send_file(LOG_FILE, as_attachment=True)


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'GET':
        return app.send_static_file('index.html')
    elif request.method == 'POST':
        file_list = request.files.getlist('files[]')
        # Return single file
        if len(file_list) < 1:
            return 'No files uploaded'
        elif len(file_list) == 1:
            file = file_list[0]
            log.info('Converting file {}'.format(file.filename))
            # Get file name and type
            filename = path.splitext(file.filename)[0]
            file_type = path.splitext(file.filename)[1].strip('.')

            try:  # Convert to markdown
                markdown = convert_text(file.stream.read(), 'md', file_type)
            except RuntimeError as e:
                if e.args[0].startswith('Invalid input format!'):
                    log.error('Invalid input format!')
                    return 'Unsupported file type: {}'.format(file_type.upper())
                else:
                    log.error(e.args[0])
                    return 'Unknown Error'

            # Send markdown file as attachment
            return Response(markdown, mimetype='text/markdown',
                            headers={'Content-Disposition': 'attachment;filename={}.md'.format(filename)})

        else:  # Return zip file
            memory_file = BytesIO()
            with ZipFile(memory_file, 'w') as zf:
                for file in file_list:
                    log.info('Converting file {}'.format(file.filename))

                    # Get file name and file type
                    filename = path.splitext(file.filename)[0]
                    file_type = path.splitext(file.filename)[1].strip('.')
                    
                    try:  # Convert to markdown
                        markdown = convert_text(file.stream.read(), 'md', file_type)
                    except RuntimeError as e:

                        if e.args[0].startswith('Invalid input format!'):
                            log.error('Invalid input format!')
                            return 'Unsupported file type: {}'.format(file_type.upper())
                        else:
                            log.error(e.args[0])
                            return 'Unknown Error'

                    # Write File to Zipfile
                    data = ZipInfo('{}.md'.format(filename))
                    data.date_time = localtime(time())[:6]
                    data.compress_type = ZIP_DEFLATED
                    zf.writestr(data, markdown)

            # Send zip file as attachment
            memory_file.seek(0)
            return send_file(memory_file, attachment_filename='Markdown.zip', as_attachment=True)


if __name__ == "__main__":
    app.run()
