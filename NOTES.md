# NOTES

## Desired Changes

Backend:
- singleton app state
- preview media saved elsewhere
- media gen worker process (w/ Muiltiprocessing queue for jobs)
- folder change listener process
- gunicorn support
- logging for various things
    - worker process
    - file listener
    - hash collisions

Frontend:
- written in Svelte (MPA)
- served by backend (static MPA site)
- typescript
- Dashboard page for
    * adding
    * tracking preview media generation status
    * initializing media generation
    * initializing rescan of directories
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
|   |-- routes/                 
|   |   |-- __init__.py
|   |   |-- api_media_router.py     `// `
|   |   |-- api_router.py           `// `
|   |   |-- search_router.py        `// `
|   |-- search/                 
|   |   |--__init__.py              `// `
|   |   |-- search.py               `// `
|   |   |-- similarity.py           `// `
|   |   |-- tfidf.py                `// `
|   |-- util/                   
|   |   |--__init__.py
|   |   |-- media.py                `// `
|   |   |-- meta.py                 `// `
|   |   |-- process.py              `// `
|   |-- __init__.py
|   |-- app_state.py                `// holding app state (to replace with db stuff)`
|-- config.py                       `// global config variables`
|-- main.py                         `// app starting point`
