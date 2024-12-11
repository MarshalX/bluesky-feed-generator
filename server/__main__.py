import logging

from app import app
from server.logger import logger

if __name__ == '__main__':
    # FOR DEBUG PURPOSE ONLY
    logger.setLevel(logging.DEBUG)
    app.run(host='127.0.0.1', port=8000, debug=True)
