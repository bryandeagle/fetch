from app import app
import os

if __name__ == '__main__':
    app.run(host=os.environ['IP'], debug=False)
