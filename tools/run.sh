#!/bin/bash

set -e

cd frontend
npm run build

cd ..
source .venv/bin/activate

python3 main.py "$@"
