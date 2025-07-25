# NOTES


## TODO


TINY_TERM:
- [frontend] add dated marker button/ui
- [frontend] add video rating

SHORT_TERM:
- [app] flesh out tray icon app
- [frontend] figure out why middle click drag opens results card hrefs
- [frontend] catalogue page: add thresh and item counts (and numbered count view)
- [media_gen] [fix] seek thumbs alignment
- [frontend] create PassionPlayer MVP

MEDIUM_TERM:
- [data] port old favourites
- [frontend] [finish] search panel

- [frontend] [finish] catalogue page
- [frontend] [finish] PassionPlayer
- [frontend] [add] search panel: list/compact list view & page result count
- [backend] Get performer (and studio) embeddings working
- [frontend] [finish] video page below section
- [frontend/backend] Redo dashboard (minimal)

LONG_TERM:
- [admin] promote to others/get others to test
- [admin] find way to make not-nsfw preview
- [app] dockerize

FAR_FUTURE:
- [db] migrate to proper column structure
- [backend] rewrite in Go

COLLECTION:
- [media] Generate preview media for entire collection
- [collection] Handle PMVHaven collection
- [collection] Handle collisions (Curated v. PH)

OPTIONAL:
- [backend] Add method of seeing tf-idf tokens
- [frontend] Add search box to nav search button
- [frontend] Make list view search result component
- [frontend] date_added/date_released dist extension
- [frontend] word cloud
- [frontend] watch history page

THEORETICAL:
- [app] Add way to make gifs
- [app] Figure out way to link to d18 (or other 18+ db)



<!-- - [app] create tray icon app MVP -->
<!-- - [frontend] add actor cards -->
<!-- - [backend] figure out way to toggle NoCacheMiddleware for dev/prod purposes -->
<!-- - [frontend] [result_card] add initial limit to actors & tags -->
<!-- - [frontend] [finish] related videos section -->
<!-- - [media] Convert entire collection to mp4 -->
<!-- - [media] Transcode non remuxable -->
<!-- - [backend] Review collection ignore/include folder step -->
<!-- - [media] Handle JAV collection -->
<!-- - [media] Handle PH collection -->
<!-- - [frontend] [new] port & clean search page -->
<!-- - [frontend] [new] port & clean video page -->
<!-- - [frontend] [new] port & clean home page -->
<!-- - [frontend] [new] port & clean dashboard page -->
<!-- - [frontend] [new] Add new search result cards -->
<!-- - [frontend] [new] Add new catalogue page -->
<!-- - [frontend] [new] Add new video page -->
<!-- - [frontend] Add nav dropdown to select search result style (for grid view) -->
<!-- - [backend] Add teaser thumbs -->
<!-- - [backend] Add preview media status -->
<!-- - [backend] Find why no similar-videos for f5593d2a6f9a -->
<!-- - [frontend] [new] get header looking like svelte header -->
<!-- - Bring over favourites & make metadata db -->
<!-- - Get tfidf model working -->
<!-- - Improve media generation -->
<!-- - Add subtitles to video -->
<!-- - Get vman script for mkv -> mp4 conversion -->
<!-- - Get seek thumbs sprite sheets working -->
<!-- - Get media generation working -->



## GO REWRITE PATH

0. Migrate DB
1. Minimal Viable Product:
  - serve media (no ensures)
  - api router
  - interact router
2. Add non-TFIDF search
  - search videos
  - get catalogue
3. Add media ensuring (w/ python)
4. Add TFIDF search stuff (w/ python)
5. Frontend scan/media control (w/ python)
6. (Optional, Discouraged) Backend manager
  - scanning
  - media generation (ffmpeg + porting opencv implementations)


## VIDEO PAGE

buttons:
- rate
- like
- add dated marker
- make gif
- extract frame (as thumbnail or something)
- chapter nav
- edit filename



- open d18 page
- open external link (ph)


info:
- date added
- show description button
- filename (copy button)
- Location parent on disk (copy button)






### ALT STRUCTURE

#   |   |   |   |   |   |   |   |   |
|-- .venv/
|-- .logs/
|-- data/
|-- frontend/               `// `
|-- backend/               `// (Empty) Future go server rewrite`
|-- src/                    `// app src`
|   |-- media/            `// `
|   |   |-- checkers.py
|   |   |-- mass_generators.py
|   |-- recommender/            `// `
|   |   |-- search.py
|   |   |-- similarity.py
|   |   |-- tfidf.py
|   |-- scan/            `// `
|   |   |-- scan.py
|   |   |-- process.py
|   |-- schemas/                `// `
|   |   |-- queries.py
|   |   |-- video_data.py
|   |   |-- video_interact.py
|   |-- server/                    `// Used by Main`
|   |   |-- api/                    `// `
|   |   |   |-- actor_api.py
|   |   |-- routers/                `// `
|   |   |   |-- api_router.py
|   |   |   |-- query_router.py
|   |   |   |-- media_router.py
|   |-- util/                    `// General utilities`
|   |   |-- db.py
|   |   |-- config.py
|   |   |-- logging.py
|   |   |-- general.py
|   |-- worker_scripts/             `// Isolated scripts run as subprocess`
|   |   |-- generateSomeMedia.py
|   |-- __init__.py
|   |-- main.py                 `// Main entrypoint, starts fastAPI`
|   |-- worker.py               `// Worker, run manually or by main as subprocess`
|-- tools/          `// Shell scripts for installing/running`
|-- tray_app/       `// Launcher App (Tray Icon)`


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



