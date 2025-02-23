# CandyPop Video (v2)

## About

My personal lightweight video viewer App! Browse local collection of videos using a *YouTube-like* web UI, search videos with powerful search panel, preview videos with generated preview media, get recommended videos under the video you're watching. 

Built with **FastAPI** + **Svelte** ❤️


## System Dependencies

- python >= 3.8
- npm
- ffmpeg
- MKVToolNix (optional, improves re-hashing speed for mkv videos)
- tmux (optional)


## Installing (Linux)

- install system dependencies & clone repo
- run `tools/install.sh`
- configure `config.yaml` (add app_data_dir and collections)


## Running (Linux)

- **option 1:** run `tools/run.sh`
- **option 2:** run `tools/run_tmux.sh` for tmux session


## Improvements from v1:
- switched from Flask --> FastApi + Uvicorn for the backend
- went from plain JS --> Svelte for the frontend
- using proper db (SQLite)
- better shell scripts for installing/running

