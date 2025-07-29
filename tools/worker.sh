#!/usr/bin/env bash

set -e

# Navigate to project directory
TOOLS_DIR="$(dirname "$(readlink -f "$0")")"
cd "$TOOLS_DIR/.."

# TODO: Needs testing!!

# Run worker
./.venv/bin/python -m python_src.worker "$@"
