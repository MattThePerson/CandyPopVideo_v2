# NOTES



## TODO

- [frontend] [new] port & refactor search page
- [frontend] [new] port & refactor video page
- [frontend] [new] port & refactor home page
- [frontend] [new] port & refactor dashboard page
- [frontend] [new] Add new catalogue page
- [frontend] Create custom video player
- [frontend] [new] Add new search result cards
- [frontend] [new] Add new search panel
- [frontend] [new] Add new video page
- [frontend] [new] Add search box to search button
- [frontend] Improve frontend terminal experience
- [media] Figure out media gen errors
- [media] Handle JAV collection
- [media] Handle PH collection
- [media] Transcode non remuxable
- [media] Convert entire collection to mp4
- [media] Generate preview media for entire collection
- [backend] Add teaser thumbs
- [backend] Get performer (and studio) embeddings working
- [backend] Add method of seeing tf-idf tokens
- [backend] Add preview media status
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



## FAVOURITES TO MANUALLY ADD

<!-- - "A:\Whispera\videos\_MainCollection\Alexis Texas\DigitalPlayground\Alexis Texas - DigitalPlayground - [2010] Girl Next Door - Scene 1 [Heather Starlet, Charles Dera] #Rimming #Threesome #DoubleBlowjob #BikiniSex.mkv" -->
<!-- - "A:\Whispera\videos\_MainCollection\Alexis Texas\_LQ\Alexis Texas - HollyRandall - [2014] Sex In The City [Toni Ribas] #LQ #BlackLingerie #LightblueSheets.mkv" -->
- "A:\Whispera\videos\_MainCollection\Alexis Texas\_LQ\Alexis Texas - RetromediaEntertainment - Bikini Frankenstein - Scene 1 (48fps, Color Graded) #PinkUndies #Classroom #HighHeels.mkv"
- "A:\Whispera\videos\_MainCollection\_ByStudio\TonightsGirlfriend\Alexis Texas - TonightsGirlfriend - Role Playing with Alexis.mkv"
- "A:\Whispera\videos\_MainCollection\Alexis Texas\ZTOD\Alexis Texas - ZTOD - [2010] Curvies - Scene 4 [Pat Myne] #WhiteLeatherCouch #Chocker.mkv"
- "A:\Whispera\videos\_MainCollection\AJ Applegate\AJ Applegate - HotBabes4k - Big Booty AJ Goes Hardcore.mkv"
- "A:\Whispera\videos\_MainCollection\AJ Applegate\AJ Applegate - BangBros - [2014] Monsters of Cock [Jack Napier].mkv"
- "A:\Whispera\videos\_MainCollection\AJ Applegate\AJ Applegate - Wicked - [2018] He Loves Me in Stockings and Heels 2 [Tyler Nixon].mkv"
- "A:\Whispera\videos\_MainCollection\AJ Applegate\SweetSinner\AJ Applegate - SweetSinner - [2016] Shades Of Kink 7 - Scene 4 [Tyler Nixon].mkv"
- "A:\Whispera\videos\_MainCollection\_ByStudio\Bellesa\AJ Applegate - BellesaFilms - [2020] I'm Cold [Damon Dice].mkv"














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
