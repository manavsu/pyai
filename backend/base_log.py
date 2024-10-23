import logging
from logging.handlers import RotatingFileHandler 
import datetime
import logging.handlers
import sys
import os

BASE_LOG = logging.getLogger("pyai")
BASE_LOG.setLevel(logging.DEBUG)

now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(level=logging.INFO)
log_path = os.path.join('log', now)

if not os.path.exists(log_path):
    os.makedirs(log_path)

file_handler = RotatingFileHandler(os.path.join(log_path, 'pyai.log'), maxBytes=1000000, backupCount=5)
file_formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.INFO)  # Set to INFO to avoid showing DEBUG messages in the console

# Add the handlers to the 'pyai' logger
BASE_LOG.addHandler(file_handler)
BASE_LOG.addHandler(console_handler)

BASE_LOG.propagate = False

logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('traitlets').setLevel(logging.WARNING)

BASE_LOG.info("Base log initialized.")