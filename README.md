# CandyPop Video (v2)

## About

My personal lightweight video viewer App! Browse local collection of videos using a *YouTube-like* web UI, search videos with powerful search panel, preview videos with generated preview media, get recommended videos under the video you're watching. 

Built with **Python FastAPI** + **JS, HTML & CSS** ❤️


## System Dependencies

- python >= 3.8
- ffmpeg
- **Linux:** libgl1
- *(Optional)* Docker Desktop


## Install & Run

You have 2 options:

### 1. Using Tray App:

- **Install system dependencies (see above)**:

- **Clone repo**:

- **Run install scripts:** \
   *Linux:* `./tools/install.sh` \
   *Windows:* `.\tools\install.ps1`

<!-- - **Run make**: \
  *Windows*: Either install GNU Make (choco install make) -->

- **Run executable**: \
  `.\CandyPopVideoTrayApp.exe` or `./CandyPopVideoTrayApp`
  

### 2. Using Docker:

- TBA


## Configuration

After installing and running, edit `config.yaml` to set:
- Desired `AppData` location
- List of video library folders (organized into collections)
- *(Optional)* edit filename formats


## Improvements from v1:
- switched from Flask --> FastApi + Uvicorn for the backend
- improved frontend UI
- using proper db (SQLite)
- better shell scripts for installing/running
- better backend manager

