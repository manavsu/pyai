import logging
from logging import FileHandler
import datetime
import logging.handlers
import sys
import os

if len(sys.argv) < 4:
    print("Usage: python fast_api.py <api_key> <agent_id> <log_path>")
    sys.exit(1)

agent_id = sys.argv[2]
log_path = sys.argv[3]

BASE_LOG = logging.getLogger("pyai")
BASE_LOG.setLevel(logging.DEBUG)

now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(level=logging.INFO)

if not os.path.exists(log_path):
    os.makedirs(log_path)

file_handler = FileHandler(os.path.join(log_path, f'{now}_{agent_id}.log'))
file_formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.INFO)

BASE_LOG.addHandler(file_handler)
BASE_LOG.addHandler(console_handler)

BASE_LOG.propagate = False

logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('traitlets').setLevel(logging.WARNING)

BASE_LOG.info(f"Base log initialized for {agent_id}.")
