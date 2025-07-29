#!/usr/bin/env bash

set -e

BACKEND_PORT=8000

# Navigate to project directory
TOOLS_DIR="$(dirname "$(readlink -f "$0")")"
cd "$TOOLS_DIR/.."


# Parse arguments
forward_args=()
REINSTALL_VENV=0
export DEV_MODE="0"

echo "args: $@"

for arg in "$@"; do
  if [[ "$arg" == "--reinstall-venv" ]]; then
    echo "[.sh] Captured '--reinstall-venv' command"
    REINSTALL_VENV=1
  elif [[ "$arg" == "--dev" ]]; then
    echo "[bash] Captured '--dev' command"
    export DEV_MODE="1"
  else
    forward_args+=("$arg")
  fi
done



# Create venv if needed
if [ ! -d ".venv" ] || [ $REINSTALL_VENV -eq 1 ]; then
    echo "[bash] Installing local python environment (.venv) ..."
    python3 -m venv .venv
    source .venv/bin/activate
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    echo "[bash] Done! Local environment created."
fi


# START
echo "[bash] Starting uvicorn on port "$BACKEND_PORT" with extra args: '"${forward_args[@]}"'"
# ./.venv/bin/uvicorn main:app --host 0.0.0.0 --workers 1 --port $BACKEND_PORT "${forward_args[@]}"
