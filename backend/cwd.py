import os
from contextlib import contextmanager

@contextmanager
def cwd(new_directory):
    original_directory = os.getcwd()
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)
    os.chdir(new_directory)
    try:
        yield
    finally:
        os.chdir(original_directory)