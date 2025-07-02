# NOTES



## TODO

<!-- - [frontend] [new] port & clean search page -->
<!-- - [frontend] [new] port & clean video page -->
<!-- - [frontend] [new] port & clean home page -->
<!-- - [frontend] [new] port & clean dashboard page -->
<!-- - [frontend] [new] Add new search result cards -->
- [frontend] [new] Add new catalogue page
- [frontend] [new] Add new search panel
- [frontend] Create custom video player
- [frontend] [new] Add new video page
- [frontend] [new] Add search box to nav search button
- [frontend] Improve frontend terminal experience
- [media] Handle JAV collection
- [media] Handle PH collection
- [media] Transcode non remuxable
- [media] Convert entire collection to mp4
- [media] Generate preview media for entire collection
- [backend/media] Figure out media gen errors
- [backend] Add teaser thumbs
- [backend] Get performer (and studio) embeddings working
- [backend] Add method of seeing tf-idf tokens
- [backend] Add preview media status
<!-- - [backend] Find why no similar-videos for f5593d2a6f9a -->
<!-- - [frontend] [new] get header looking like svelte header -->
<!-- - Bring over favourites & make metadata db -->
<!-- - Get tfidf model working -->
<!-- - Improve media generation -->
<!-- - Add subtitles to video -->
<!-- - Get vman script for mkv -> mp4 conversion -->
<!-- - Get seek thumbs sprite sheets working -->
<!-- - Get media generation working -->



CatalogueQuery:
  - type: [performers|sort-performers|studios|collections|tags]
  - query_string: str
  - filter_performer: str
  - filter_studio: str
  - filter_collection: str
  - filter_tag: str


CatalogueResponse:
  - performers:  [ (name, scenes), ... ]
  - studios:     [ (name, scenes), ... ]
  - collections: [ (name, scenes), ... ]
  - tags:        [ (name, scenes), ... ]


/query/get/catalogue/{CatalogueQuery}



## METADATA DB


- favourite
- views
- likes
- rating [S+|S|A|B+|B-|C]
- markers
- i_came_markers
- user_comments














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
