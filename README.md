# CandyPop Video (v2)

## About

My personal lightweight video viewer App! Browse local collection of videos using a *YouTube-like* web UI, search videos with powerful search panel, preview videos with generated preview media, get recommended videos under the video you're watching. 

Built with **FastAPI** + **Svelte** ❤️


## System Dependencies

- python >= 3.8
- npm
- Node.js (18.13 or higher for Svelte)
- ffmpeg


## Installing

- clone repo & install system dependencies
- run `tools/install.sh` (Linux) or `tools\install.bat` (Windows)
- configure `config.yaml` (add app_data_dir and collections)


## Running

- **Linux:**   `./tools/run.sh`
- **Windows:** `.\tools\run.ps1`


## Improvements from v1:
- switched from Flask --> FastApi + Uvicorn for the backend
- went from plain JS --> Svelte for the frontend
- using proper db (SQLite)
- better shell scripts for installing/running

