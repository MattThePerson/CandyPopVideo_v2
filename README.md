# CandyPop Video v2

## About

My personal lightweight video viewer App! Built with Python + Svelte ❤️

Improvements from v1:
- switched from Flask --> FastApi + Uvicorn for the backend
- went from plain JS --> Svelte for the frontend
- better shell scripts for installing/running

## System Dependencies

- python >= 3.8
- npm
- ffmpeg
- MKVToolNix (optional, improves re-hashing speed for mkv videos)
- tmux (optional)

## Installing (Linux)

- install system dependencies & clone repo
- run `tools/install.sh`

## Running (Linux)

- (either) run `tools/run.sh`
- (or) run `tools/run_tmux.sh` for tmux session
