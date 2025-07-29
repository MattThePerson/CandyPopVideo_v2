# CandyPop Video (v2)

**IMPORTANT**: This project and README are incomplete!

## About

My personal local video viewer App! Browse local collection of videos using a *YouTube-like* web UI, search videos with powerful search panel, get recommended videos under the video you're watching. 

Built with **Go** + **Python** + **JS** ❤️


## System Dependencies

- python >= 3.8
- go >= 1.21
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

- (Alternative, no tray app) **Run backend directly** \
  `.\go_backend\CandyPopVideo.exe`

### 2. Using Docker:

(Temporary manual method)

#### **Build:**

Clone the repo then run: `docker build -t cpop-vids .`

#### **Run:**
You must mount volumes for AppData, Video Libraries and config.yaml. 


*PowerShell example:*
```
docker run `
-v "A:/videos:/app/videos" `
-v "A:/.AppData/CandyPopVideo:/app/appdata" `
-v "${PWD}/config.yaml:/app/config.yaml" `
-p 8013:8013 cpop-vids
```


## Configuration

After installing and running, edit `config.yaml` to set:
- Desired `AppData` location
- List of video library folders (organized into collections)
- *(Optional)* edit filename formats

## Backend Worker (scanning/preview media generation)

To explore your videos with the app you need to scan them and generate preview media. The best way to (currently) do this is by running `.\tools\worker.ps1` (or `./tools/worker.sh` on linux) in the project root. 

#### Useful commands

| CMD | DESCRIPTION |
|--|--|
| `--scan-libraries` | Scan videos from media directories defined in `config. yaml` |
| `--status` | Status of scanned videos (per collection) |
| `--generate-media all` | Generated preview media by given type |
| `--media-status all` | Status of generated preview media by given type |
| `-f` | Filter which videos to use when scanning/generating media |
|  |  |
| `--update-media <HOURS>` | Generates media for videos *added* (via file creation time) in the last x `HOURS` |
| `--update <FILTER>` | Scan and generate media for all videos that contain the given `FILTER` |

To get the full list of args, use `--help`.


