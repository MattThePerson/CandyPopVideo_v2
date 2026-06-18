# CLAUDE.md

## Responsibilities

### Formatting

For all fucking files use 4 fucking spaces for tabsize.

Svelte-specific formatting rules live in `frontend/CLAUDE.md`.

### Refactor

This project is undergoing a staged refactor. Claude's role is to implement each stage in order, following the plan in `docs/PROGRESS.md`. Responsibilities:

- Keep `docs/PROGRESS.md` up to date as items are completed or the plan changes.
- Work stage by stage; don't pull in Stage 3/4 concerns while Stage 1 is active.
- When completing a stage, note it in `docs/PROGRESS.md` and flag it to the user before moving on.
- The current active stage is **Stage 1 (Full Svelte Frontend)**.

### File length

Keep files under ~200 lines wherever practical. If a Svelte component, page, or module grows significantly past this, extract sub-components, helper utilities, or logic modules rather than continuing to accumulate in one file. This is a soft limit — some files legitimately exceed it — but it should prompt a decomposition check.

### Updating CLAUDE.md

In order to maintain sync between the project and this document, Claude keeps it up to date as follows:

- **`## Responsibilities` / `## About`** — Claude does not edit these unless told explicitly, *except* for meta-updates to this `Updating CLAUDE.md` subsection itself (e.g. adjusting which sections are kept in sync).
- **`## <other>`** — Claude actively keeps this current: stack, backend/frontend structure, build tooling, conventions. Update it whenever the tech stack, dependencies, or file/module layout change meaningfully.
- **`frontend/CLAUDE.md`** — Claude keeps this in sync with Svelte/frontend conventions. Update it when frontend formatting rules or component conventions change.

## About

CandyPop Video is a personal, self-hosted local video library application. You point it at folders of video files; it scans them, derives structured metadata from filenames (and optional JSON sidecar files), hashes each video for stable identity, and serves a YouTube-style web UI for browsing, searching, and watching the collection. On top of the raw library it tracks per-video interactions — favorites, ratings, view time, timestamped markers, comments — and offers TF-IDF-based "similar videos" recommendations.

It's built and run as a single-user local web app: no auth, no multi-tenancy, just a server you start and a browser tab you open.

## Tech Stack

- **Go backend** (`go_backend/`) — [Echo v4](https://echo.labstack.com/) HTTP server. This is the actively developed server.
- **Python backend + worker** (`python_src/`) — a FastAPI server (`main.py`) that mirrors the Go server's route layout, plus a CLI tool (`worker.py`) for library scanning, TF-IDF model building, and media generation. The Go server shells out to small Python scripts for functionality not yet native to it.
- **Frontend** (`frontend/`) — Svelte 5 + TypeScript + Tailwind v4, Vite-built. The active frontend served by the Go backend. (The old vanilla JS frontend is preserved at `frontend_old/` for reference.)
- **SQLite** — the only data store. Both backends talk to it directly (Go via `modernc.org/sqlite`, a pure-Go driver so no CGO toolchain is needed).
- **ffmpeg** — required system dependency; used directly for poster frames, video "teasers", thumbnail spritesheets, and mkv→mp4 remuxing.
- **handymatt / handymatt-media** — the author's own Python libraries, used for video hashing and WSL-aware path conversion.
- **launcher** (`launcher/`) — a `pystray` tray-icon app that wraps the server process so it can be started/stopped/restarted without a terminal window.

## Architecture

Two backend implementations currently coexist, with a CLI worker alongside them:

1. **Go server** (`go_backend/main.go`, entrypoint built to `bin/CandyPopVideo.exe`) — the primary server. Serves the frontend as static files, owns all database reads/writes, and exposes routes grouped under `/media`, `/api`, `/api/query`, and `/api/interact`. Started directly or via the tray-app launcher.
2. **Python server** (`python_src/main.py`, FastAPI + uvicorn) — the original implementation, kept route-compatible with the Go server (`/media`, `/api`, `/api/query`, `/api/interact`). Functionally a reference/fallback for routes the Go server doesn't yet implement.
3. **Python worker** (`python_src/worker.py`, run as `python -m python_src.worker <flags>`) — not a server. A CLI for scanning libraries into the DB, building the TF-IDF recommendation model, and mass-generating preview media. Driven manually or via `tools/worker.ps1` / `tools/worker.sh`. See `--help` for the full flag set (`--scan-libraries`, `--generate-media`, `--status`, `--update <filter>`, `--update-media <hours>`, etc).

Where the Go server needs functionality not yet ported, it shells out to standalone Python scripts in `python_src/worker_scripts/` and parses their stdout as JSON (see `execPythonSubprocess` / `execPythonSubprocess_Output` in `go_backend/internal/routes/0_routes_helpers.go`). This currently covers: actor info lookups, similar-video recommendations (TF-IDF), and on-demand preview-media generation (teasers, spritesheets). The Python interpreter used is whatever lives in the project's `.venv`.

## Directory Structure

```
go_backend/             # Go HTTP server (Echo)
    main.go             # entrypoint, route registration, static file serving
    config.go           # config.yaml loader
    internal/
        db/             # sqlite access + in-memory video cache
        schemas/        # VideoData, VideoInteractions, query structs
        query/          # search filtering/sorting, catalogue aggregation
        routes/         # media / api / query / interact route handlers

python_src/             # Python FastAPI server + CLI worker
    main.py             # FastAPI app (route-compatible with go_backend)
    worker.py           # CLI entrypoint: scan / generate media / TF-IDF / status
    scan/                # filesystem walking + filename/metadata parsing
    media/               # ffmpeg-based preview media generation + status checks
    recommender/         # TF-IDF model building, search, similarity
    schemas/             # VideoData / VideoInteractions / query dataclasses (Python side)
    server/routers/      # FastAPI routers mirroring go_backend's route groups
    worker_scripts/      # standalone scripts invoked as subprocesses by Go
    util/                # config loading, db helpers, logging

frontend/               # Svelte 5 + TS + Tailwind v4 frontend (Vite-built, served by Go backend)
    src/
        lib/
            router/      # hand-rolled client-side router (routes.ts, router.svelte.ts)
            types/       # VideoData, VideoInteractions, SearchQuery, CatalogueQuery (TS interfaces)
            stores/      # settings.svelte.ts — cardVariant/cardSize/teaserMode, persisted to localStorage
            util/        # pager.svelte.ts — createPager() batch-paging helper
            components/  # Header.svelte, Footer.svelte, Spinner.svelte
                cards/   # DefaultCard.svelte (full video card), VideoCard.svelte (variant wrapper)
        pages/<name>/    # one folder per page: Page.svelte (home, search, catalogue, curated, video, dashboard)
        assets/fonts/    # Jaro/Inter TTFs used by app.css @font-face rules
        App.svelte       # mounts Header/Footer + routed page
        app.css          # Tailwind v4 @theme tokens + @font-face rules + body base styles

frontend_old/           # original vanilla JS frontend (reference only, no longer served)
    pages/<name>/        # one folder per page: page.html + script.js + styles.css
    shared/
        components/      # injected HTML fragments (Header, Footer, ...)
        web_components/  # custom elements (search panel, result cards, icons)
        libraries/       # PassionPlayer (video player) + other vendored JS
        util/            # component injection, fetch helpers, VTT parsing

launcher/               # pystray tray-icon app + subprocess ProcessManager
tools/                  # install/run/worker scripts (.ps1 for Windows, .sh for Linux), Makefiles
assets/                 # app/tray icons
data/                   # static data files (e.g. English stopwords for TF-IDF)
config.yaml             # runtime configuration (see below)
```

## Configuration

Runtime config lives in `config.yaml` at the project root (kept out of git via `git update-index --assume-unchanged` rather than `.gitignore`, since a real path-bearing copy has to exist locally). Both backends read it directly — the Go side via `go_backend/config.go`, the Python side via `python_src/util/config.py`.

Key fields:

- `app_data_dir` — where the app stores everything it generates: the SQLite DB (`app.db`), the TF-IDF model pickle, preview media, and actor-info cache. Library video files themselves are never touched/moved.
- `video_extensions` — which file extensions count as videos when scanning.
- `scene_filename_formats` — an ordered list of pattern templates (most-specific first) used to parse structured metadata (performers, studio, title, year, release date, source id, ...) straight out of filenames. The first pattern that matches a given filename wins.
- `collections` — maps a collection name to one or more absolute folder paths. A path prefixed with `!` is scanned for exclusion only (its contents are ignored even if nested inside an included path).
- `subtitle_folders` — extra folders to search for `.srt` files when serving subtitles.
- `datetime_format` — display format for dates in the frontend.

## Data Model

Videos are identified by a **content hash**, not by file path or filename — the schema-level comment in `go_backend/internal/schemas/video_interactions.go` and the use of hash as primary key throughout reflects that paths are expected to change (renames, moves, drive reshuffles) while the hash-keyed metadata and interaction history must survive that. Scanning re-uses the existing hash for a path it already knows about and only re-hashes when a file's path can't be matched to an existing record.

SQLite is used unconventionally: rather than normalized columns, each table (`videos`, `interactions`) stores one row per video keyed by `id` (the hash) with a single `data` column holding a JSON blob of the full struct (see `ReadSerializedRowFromTable` / `WriteSerializedRowToTable` in `go_backend/internal/db/db.go`). A `views` table is the one exception — it's appended to as a plain log of `(timestamp, video_hash, duration_sec)` rows rather than serialized. The DB runs in WAL mode for concurrent reads/writes. The Go server also keeps a short-lived in-process cache of the entire deserialized `videos` table (`internal/db/cache.go`) to avoid re-parsing JSON on every request — it's invalidated after a base timeout *and* no further access within an access timeout.

**`VideoData`** (`go_backend/internal/schemas/video_data.go`, mirrored in `python_src/schemas/video_data.py`) — everything derived from the file itself plus parsed/external metadata:
- identity/file info: `hash`, `path`, `filename`, `date_added`, `duration`, `filesize_mb`, `fps`, `resolution`, `bitrate`, `is_linked` (false if the file backing this record can no longer be found on disk)
- collection placement: `collection`, `parent_dir`, `path_relative`
- scene/title metadata: `title`, `scene_title`, `scene_number`, `movie_title`, `movie_series`, `studio`, `line`, `date_released`, `description`, `dvd_code`, `source_id`
- people: `actors`, `primary_actors`, `secondary_actors`
- classification: `tags` (plus provenance-tracked variants from filename/path/JSON sidecar), `genres`
- crawled stats: `views`, `likes`
- `metadata` — an open-ended map for anything that doesn't have a dedicated field, typically loaded from a per-video/per-folder JSON sidecar file

**`VideoInteractions`** (`go_backend/internal/schemas/video_interactions.go`) — everything generated by *watching* the video, keyed by the same hash:
- `last_viewed`, `viewtime` (cumulative seconds), `is_favourite` / `favourited_date`, `likes`
- `rating` (a letter grade `C` through `S+`) and a derived `rating_score` for numeric sorting
- `markers` — `(video_time, color, tag)` tuples for arbitrary annotated points in the video
- `dated_markers` — `(video_time, datetime)` pairs
- `comments` — `(comment, datetime)` pairs

## Backend Subsystems

**Scanning** (`python_src/scan/`) — walks all configured collection folders, filters by extension and ignore-list, hashes new/changed files, and parses each filename against `scene_filename_formats` to populate `VideoData`. Existing DB records are merged with freshly scanned ones rather than replaced outright, so manually-edited fields and interaction history aren't clobbered. Videos no longer found on disk are marked `is_linked: false` rather than deleted, so their interaction history (favorites, ratings, view time) is preserved if the file reappears (e.g. on a reconnected drive).

**Media generation** (`python_src/media/`, invoked either via the worker CLI or on-demand by the Go server's `/media/ensure/*` routes) — ffmpeg-driven generation of poster frames, short "teaser" preview clips, and thumbnail spritesheets (both a small "teaser thumbs" set and a dense "seek thumbs" set used for scrubbing). Generated media is cached to disk under `app_data_dir`, keyed by video hash, and only regenerated if missing or `--redo-media-gen` is passed.

**Search & recommendations** (`python_src/recommender/`) — builds a TF-IDF model (scikit-learn `TfidfVectorizer` + Snowball stemming, English stopwords from `data/stopwords_eng.txt`) over tokens extracted from each video's metadata, used for free-text search ranking and "similar videos" lookups via cosine similarity. The model + matrix are pickled to `app_data_dir` and rebuilt whenever the worker scans libraries or is told to regenerate it explicitly.

**Filtering/sorting/catalogue** (`go_backend/internal/query/`) — the Go-native, non-TF-IDF half of search: structural filtering by actor/studio/collection/tags/date ranges/favorites, configurable sort (including a natural-sort-aware title comparator that treats embedded numbers as numbers, see `formatStringForIntComparability`), and catalogue aggregation (grouping videos by actor/studio/collection/tag with counts and "newest video" info for browsing pages).

**Media serving quirks** — non-mp4/webm containers (notably `.mkv`) aren't directly playable in a `<video>` element, so the Go server pipes them through `ffmpeg -c copy -movflags frag_keyframe+empty_moov -f mp4` on the fly rather than transcoding the whole file up front.

## Frontend

No build step, no framework — plain JS modules and hand-written custom elements, loaded directly by the browser. Structure:

- `pages/<name>/` — one folder per route (`home`, `search`, `catalogue`, `video`, `dashboard`, ...), each with its own `page.html`, `script.js`, and `styles.css`. Folders suffixed `_new`/`_old` mark in-progress rewrites of a page living alongside the version currently in use.
- `shared/components/` — small functions returning HTML strings, injected into `<custom-header>`/`<custom-footer>` placeholder elements at load time by `shared/util/component.js` (a homegrown component system — not a templating library).
- `shared/web_components/` — real custom elements (`customElements.define`), e.g. the search panel and search-result-card variants.
- `shared/libraries/` — vendored/in-house JS, most notably **PassionPlayer**, a custom `<video>`-element-based player supporting editable timeline markers/annotations (the backing store for `VideoInteractions.markers`/`dated_markers`).
- A tiny Express dev server (`frontend/package.json`: `express` + `http-proxy-middleware`) exists for local frontend iteration with API requests proxied to a running backend; in normal operation the frontend is just served as static files by whichever backend (Go or Python) is running.

## Launcher

`launcher/tray_app.py` + `launcher/ProcessManager.py` wrap the server executable in a system tray icon (start/stop/restart, log to a rotating file handler) so the app can run unattended without a visible console. Packaged to a standalone executable via PyInstaller (`make build-launcher` / the `build` target in `tools/Windows.mak` / `tools/Linux.mak`).

## Build & Run

- `make install` — creates `.venv`, installs `requirements.txt` (via `uv` for speed).
- `make build-go` — builds the Go server to `bin/CandyPopVideo.exe` (or unsuffixed on Linux).
- `make build-launcher` — packages the tray app to `bin/CandyPopVideoTrayApp.exe` via PyInstaller.
- `make build` — both of the above.
- `tools/run_go.ps1` / equivalent — runs the built Go server.
- `tools/run_python.ps1 [--dev] [--reinstall-venv]` — runs the Python FastAPI server directly via uvicorn (creates `.venv` on first run if missing).
- `tools/worker.ps1` / `tools/worker.sh` — runs the Python worker CLI (`python -m python_src.worker`) with whatever args are forwarded.
- Both Makefiles are OS-gated through the root `Makefile`, which includes `tools/Windows.mak` on Windows and `tools/Linux.mak` otherwise.
- Docker is also supported as an alternative to the tray app/native install — see `Dockerfile`; requires mounting `app_data_dir`, the video library paths, and `config.yaml` as volumes.

## Known Gaps / In-Progress Areas

(See `NOTES.md` for the live, unfiltered TODO list.) Notable unfinished or partial pieces as of now:

- Several Go routes are explicit stubs (`501 Not Implemented`): curated collections, similar-actors, similar-studios, marker get/update.
- TF-IDF-ranked sorting of free-text search results isn't wired up on the Go side yet (`ECHO_search_videos` filters/sorts structurally but doesn't yet call into the TF-IDF subprocess for the `search_string` case).
- Performer/studio embeddings (for "similar actor/studio" features) are a planned but unimplemented worker feature (`--generate-embeddings` is a no-op stub).
- A handful of frontend pages exist in parallel old/new versions (e.g. `dashboard` vs `dashboard_old`, `search` vs `search_new`, `video` vs `video_new`) as features are reworked in place.

## Svelte rewrite

The vanilla-JS frontend (preserved at `frontend_old/` for reference) is being replaced by `frontend/` — a Svelte 5 + TypeScript + Tailwind v4 project (Vite-built, no SvelteKit). The header chrome, client-side router, card system, and home page are all functional; the remaining five pages (`search`, `catalogue`, `curated`, `video`, `dashboard`) are stubs.

- **Router** (`src/lib/router/`) — hand-rolled, no third-party package, real URL paths (history mode, not hash routing):
  - `router.svelte.ts` — `routerState` (`$state`-backed current path), `navigate(path, { replace? })`, `initRouter()` (wires `popstate` + a delegated `document` click listener that intercepts same-origin `<a>` clicks and routes them client-side, skipping modifier-clicks/`target`/`download`/external links), and `matchRoute`/`matchPattern` (segment-based matching with `:param` support, ready for future params like `/video/:hash`). The `.svelte.ts` suffix is required for top-level rune usage outside a `.svelte` file.
  - `routes.ts` — ordered `{ pattern, component }` table, checked first-match-wins.
  - `App.svelte` calls `initRouter()` on mount, derives the current match via `matchRoute(routerState.path)`, and renders `<Header />` / the matched page (spreading params as props) / `<Footer />`.
- **Components** (`src/lib/components/`):
  - `Header.svelte` — logo, home/search/catalogue/curated nav links, shuffle/search/dashboard/settings icon buttons, active-link highlighting driven by `routerState.path`. Scoped `<style>` for logo font sizing, active-link colour, dropdown positioning.
  - `Footer.svelte` — simple copyright line.
  - `Spinner.svelte` — reusable orange gradient ring animation. Props: `size` (px, default 52) and `bg` (inner-circle colour matching the container background, default `#060A0A`). Used inside card thumbnails while the spritesheet is loading, and on pages while data fetches are in flight.
  - `cards/DefaultCard.svelte` — the full video card. Poster image with a hover sprite-sheet teaser (fires `/media/ensure/teaser-thumbs-small/:hash`, then loads the VTT + spritesheet and scrubs by mouse position); stats overlay (resolution/bitrate/duration chips, views, collection badge, NEW badge); interactions loaded from `/api/interact/get/:hash` (viewtime, likes, rating, favourite toggle with optimistic UI); actor/tag lists with expand-on-click for overflow; four size variants driven by the `size` prop ('small' 20.5rem / 'medium' 25rem / 'large' 33rem / 'xl' 40rem). While hovering and loading the spritesheet the poster is hidden and a `Spinner` is shown centred on the black thumbnail background; unhovered it shows the poster normally.
  - `cards/VideoCard.svelte` — thin wrapper that selects card variant via `settings.cardVariant` (currently only 'default') and passes through `video`, `size`, `width`, `aspectRatio` props.
- **Types** (`src/lib/types/`):
  - `video.ts` — `VideoData` and `VideoInteractions` TypeScript interfaces, mirroring the Go schemas.
  - `query.ts` — `SearchQuery` and `CatalogueQuery` interfaces.
- **Stores / utilities** (`src/lib/stores/`, `src/lib/util/`):
  - `settings.svelte.ts` — singleton `settings` object persisted to `localStorage`. Fields: `cardVariant` ('default'), `cardSize` ('small'|'medium'|'large'|'xl'), `teaserMode` ('sprite'|'video').
  - `pager.svelte.ts` — `createPager<T>(source, batchSize)` factory. Exposes `visible` (current slice), `hasMore`, `loadMore()`, `reset()`. Used by the home page for "Load More Results".
- **Pages** (`src/pages/<name>/Page.svelte`) — `home`, `search`, `catalogue`, `curated`, `video`, `dashboard`. The home page is fully functional: fetches a random spotlight video and renders it as a full-width `VideoCard` (21:9 aspect ratio), then fetches similar videos and shows them in a paginated card grid, with a `Spinner` during both loading phases. The remaining five pages are single-line stubs.
- Colors/fonts: `src/app.css` defines a global dark `body` background (`#060A0A`), a Tailwind v4 `@theme` block with `--color-*` tokens, and `@font-face` rules for `Jaro-Regular.ttf` and the Inter variable font (copied into `src/assets/fonts/`).
- The Go server serves `frontend/dist/assets` and `favicon.svg` directly, then falls back to `frontend/dist/index.html` for any other GET request so client-side routes survive a hard refresh/deep link.
- The Vite dev server proxies `/api`, `/media`, and `/static` to `http://localhost:8124` (the Go backend port, set in `config.yaml`) so API calls work during `npm run dev` without CORS issues.
- There's no Makefile/tooling integration yet — building means running `npm install` / `npm run build` manually inside `frontend/` (no `make build-frontend` target exists).
- A work-in-progress copy of the video player to be ported in is kept at `_ref/passion_player/` (`PassionPlayer.js` + `.d.ts`), copied from the author's separate Wails-based "Lucid Media Player" project — note its `.d.ts` still imports Wails-generated types (`wailsjs/go/models`) that won't resolve here and will need adapting. `_ref/` as a whole is gitignored (root `.gitignore`'s `_*/` rule) and also holds `VIDEO_HASHING.md`, a language-agnostic spec of the video hashing algorithm for cross-project interop.
