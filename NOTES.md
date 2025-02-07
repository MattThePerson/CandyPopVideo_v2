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
