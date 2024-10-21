#!/bin/bash

if [ ! -d ".venv" ]; then
    echo ".venv directory does not exist. Creating .venv..."
    python3 -m venv .venv
    echo ".venv created successfully."
else
    echo ".venv directory already exists."
fi

cd frontend
npm install
npm run build

cd ../backend

pip install -r requirements.txt

echo "Build completed successfully."
