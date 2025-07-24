#!/bin/bash
# Installs npm and python deps
# TODO: Update to match install.ps1

# cd into scripts parent parent directory

cd frontend
npm install
cd ..

# create venv if doesnt exist
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt
