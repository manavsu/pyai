# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

# Warning: A port below 1024 has been exposed. This requires the image to run as a root user which is not a best practice.
# For more information, please refer to https://aka.ms/vscode-docker-python-user-rights`
EXPOSE 80

ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY backend/requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

RUN mkdir -p /app/tmp && chmod a+rwx /app/tmp

RUN python -m ipykernel install --user --name=.venv --display-name "Python (.venv)"

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD [ "python", "backend/main.py" ]
