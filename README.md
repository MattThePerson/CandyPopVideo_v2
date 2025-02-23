# CandyPop Video v2

## About

My personal lightweight video viewer App! Built with FastAPI + Svelte ❤️

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

## Configure
- rename `video_folders_template.yaml` to `video_folders.yaml` and configure
- 

## Running (Linux)

- (either) run `tools/run.sh`
- (or) run `tools/run_tmux.sh` for tmux session
