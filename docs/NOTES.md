
# TODO


SHORT_TERM:
- [frontend] add dated marker button/ui
- [frontend] add video rating
- [frontend] add comments
- [frontend] figure out why middle click drag opens results card hrefs
- [frontend] create PassionPlayer MVP

MEDIUM_TERM:
- [frontend] [finish] search panel
- [frontend] [search] add "similar to video" feature (and right click menu)
- [frontend] [finish] catalogue page
- [frontend] [finish] PassionPlayer
- [frontend] [add] search panel: list/compact list view & page result count
- [backend] Get performer (and studio) embeddings working
- [frontend] [finish] video page below section
- [frontend|backend] Redo dashboard (minimal)
- [backend/worker] Add include tags from actors
- [backend/worker] Generate tags based on number/type of actors

LONG_TERM:
- [admin] promote to others/get others to test
- [admin] make sfw preview

COLLECTION:
- [media] Generate preview media for entire collection
- [collection] Handle PMVHaven collection
- [collection] Handle collisions (Curated v. PH)

OPTIONAL:
- [recommender] Add method of seeing tf-idf tokens
- [frontend] Add search box to nav search button
- [frontend] Make list view search result component
- [frontend] date_added/date_released dist extension
- [frontend] word cloud
- [frontend] comment/interact history page

THEORETICAL:
- [app] Add way to make gifs
- [app] Figure out way to link to d18 (or other 18+ db)


<!-- - [frontend] add edit favourite add date -->
<!-- - [collection] Figure out way to add popularity score -->
<!-- - [app] flesh out (and fix) tray icon app -->
<!-- - [backend] rewrite in Go -->
<!-- - [collection] Handle 3dh collection -->
<!-- - [data] port old favourites -->
<!-- - [media_gen] [fix] seek thumbs alignment -->
<!-- - [frontend] [catalogue_page] Sort by newest added video -->
<!-- - [frontend] [catalogue_page] add thresh and item counts (and numbered count view) -->
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


# DB LOCKED INSTANCES
- 2025/08/04 14:04:02 🚨🚨 ERROR 🚨🚨:  [/api/interact/get/:video_hash] Unable to read interactions row: database is locked (261)


# GO REWRITE PATH

<!-- - [go] fix sort by title -->
<!-- - [go] fix sorting of search results -->
<!-- - [go] add sorting by interactions -->
<!-- - [go] get interactions working -->
<!-- - [go] get TFIDF stuff working -->
<!-- - [go] add get actor info -->
<!-- - [go] add get spotlight video -->
<!-- - [go] get catalogue page working -->
<!-- - [go] get enforce media working -->
<!-- - [go] get recommender working -->
<!-- - [go] write go backend demo -->


<!-- 1. Minimal Viable Product: -->
  <!-- - serve media (no ensures) -->
  <!-- - api router -->
  <!-- - interact router -->
<!-- 2. Add non-TFIDF search -->
  <!-- - search videos -->
  <!-- - get catalogue -->
<!-- 3. Add media ensuring (w/ python) -->
<!-- 4. Add TFIDF search stuff (w/ python) -->
5. Frontend scan/media control (w/ python)
6. (Optional, Discouraged) Backend manager
  - tfidf recommender system
  - scanning
  - media generation (ffmpeg + porting opencv implementations)



# VIDEO PAGE

[BUTTONS]
- LIKE: way to see like count
- RATE: dropdown
- FINISHED: also see (and jump to) previous points
- JUMP TO RANDOM TIME

- CHAPTER NAV
- ADD CHAPTER

<!-- - make gif -->

[INTERACTION_INFOS]
- [inter] favourited date (edit)
- [inter] dated markers (remove)
- [inter] viewtime
- [inter] last viewed

[VIDEO_INFOS]
- date added
- filename (edit)
- parent dir path (copy)
- d18 page (open)
- extern link (open)

[UNKNOWN]
- comments (add)

[MISSING]:
- tags
- description

[MISC]
- [idea] extract frame (as thumbnail or something)

[CUSTOM_TAGS]
- early memory
- first actor video
- 


# ALT STRUCTURE

|-- .venv/
|-- .logs/
|-- data/
|-- frontend/               `// `
|-- go_backend/               `// (Empty) Future go server rewrite`
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




# Routes

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



