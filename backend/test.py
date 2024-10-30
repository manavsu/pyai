import subprocess
from cwd import cwd

with cwd("tmp"):
    subprocess.check_call(["python", "-m", "venv", ".venv"])
    subprocess.check_call([".venv/bin/pip", "install", "openai", "nbclient", "nbformat", "ipykernel"])
    subprocess.check_call([".venv/bin/python","-m", "ipykernel", "install", "--name=venv", "--display-name", "Python (venv)", "--prefix", ".venv"], text=True)
    subprocess.check_call([".venv/bin/python", "main_agent.py"])
    