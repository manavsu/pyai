import logging
from logging.handlers import RotatingFileHandler 
import datetime
import sys
import os

BASE_LOG = logging.getLogger("pyai")
now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(level=logging.INFO)
logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
logging.Filter(BASE_LOG.name)
log_path = sys.path.join('log', now)

if not os.path.exists(log_path):
    os.makedirs(log_path)

handler = RotatingFileHandler(sys.path.join(log_path, 'pyai.log'), maxBytes=1000000)
                              
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

BASE_LOG.addHandler(handler)
