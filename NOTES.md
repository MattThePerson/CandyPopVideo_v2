# NOTES

## Running via PM2 (Node.js)

Install and check:
`npm install -g pm2`
`pm2 -v`

Start and manage:
`pm2 start script.bat --name NAME`
`pm2 stop NAME`
`pm2 restart NAME`
`pm2 delete NAME`

Start powershell script:
`pm2 start powershell.exe --name NAME -- -ExecutionPolicy Bypass -File "script.ps1"`
pm2 start powershell.exe --name candypop-video -- -ExecutionPolicy Bypass -File tools\run.ps1

View status and logs:
`pm2 [list|ls|status]`
`pm2 logs NAME`
`pm2 logs --lines 200 NAME`

Persist processes on reboot:
`pm2 startup`
`pm2 save`



## Desired Changes

Backend:
- media gen worker process (w/ Muiltiprocessing queue for jobs)
- logging for various things
    - worker process
    - file listener
    - hash collisions
<!-- - dataclass for video objects -->
<!-- - preview media saved elsewhere -->

Frontend:
- written in Svelte (MPA)
- served by backend (static MPA site)
- written in typescript
- Dashboard page for
    * app status
    * scanning / rescanning
    * start media generation
    * media generation status
    * adding site-wide content filters (eg. Studio, Category, Performer)
- 



## Other

main() stages:
- load existing data and collections from json and txt files
- loads and processes videos
- loads/generates video/performer TF-IDF profiles
- [REMOVE] optionally generates preview media


## Routes

  `/`   // frontend

  `/video/{video_hash}` // serve video via FileResponse

  `/media`              // Static files for preview media

  `/api`
`/get-video-data/{video_hash}`              // get data for video

`/get-random-video`
`/get-random-video-seeded/{seed}`
`/get-random-spotlight-video`

`/add-favourite/{video_hash}`
`/remove-favourite/{video_hash}`
`/is-favourite/{video_hash}`

`/get-performers`
`/get-studios`

  `/api/media/`
`/get-seek-thumbnails/{video_hash}`
`/get-poster/{video_hash}`
`/get-preview-thumbnails/{video_hash}`
`/get-teaser-small/{video_hash}`
`/get-teaser-large/{video_hash}`

  `/search/`
`/search-videos`
`/get-similar-videos/{video_hash}/{start_from}/{limit}` // get similar videos based on tf-idf
`/get-similar-performers/{performer}`                   // get similar performers based on profile (mean video profile) similarity
`/get-similar-studios/{studio}`



### PYTHON SCRIPTS

|-- backend/
|   |-- routes/                 `// api routes`
|   |   |-- __init__.py
|   |   |-- api_media_router.py     `// `
|   |   |-- api_router.py           `// `
|   |   |-- search_router.py        `// `
|   |-- search/                 `// search & similarity`
|   |   |--__init__.py
|   |   |-- search.py               `// `
|   |   |-- similarity.py           `// `
|   |   |-- tfidf.py                `// `
|   |-- util/                   `// `
|   |   |--__init__.py
|   |   |-- media.py                `// `
|   |   |-- meta.py                 `// `
|   |   |-- process.py              `// `
|   |-- app_state.py            `// holding app state (to replace with db stuff)`
|-- config.py               `// global config variables`
|-- main.py                 `// app starting point`
