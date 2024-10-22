import os
from contextlib import contextmanager

@contextmanager
def cwd(new_directory):
    original_directory = os.getcwd()
    original_juypter_path = ""
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)
    os.chdir(new_directory)
    os.environ['JUPYTER_PATH'] = os.path.abspath(os.getcwd())
    try:
        yield
    finally:
        os.chdir(original_directory)
        os.environ['JUPYTER_PATH'] = original_juypter_path