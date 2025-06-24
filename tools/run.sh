#!/bin/bash

set -e

BACKEND_PORT=8000

# Navigate to project directory
TOOLS_DIR="$(dirname "$(readlink -f "$0")")"
cd "$TOOLS_DIR/.."

# ARGS
EXTRA_ARGS=""
if [[ "$1" == "reload" ]]; then
    EXTRA_ARGS="--reload"
    shift
fi

# BUILD FRONTEND
# cd frontend
# echo "[NPM] Building frontend"
# npm run build
# cd ..

# CHECK VENV
if [ ! -d ".venv" ]; then
    echo "[VENV] No venv created, run 'tools/install.sh'"
    exit 1
fi

# START
echo "[START] Starting uvicorn on port $BACKEND_PORT and extra args: '$EXTRA_ARGS'"
./.venv/bin/uvicorn main:app --host 0.0.0.0 --workers 1 --port $BACKEND_PORT $EXTRA_ARGS

# ./.venv/bin/python main.py "$@"
