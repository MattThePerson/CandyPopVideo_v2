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

- **Go backend** (`go_backend/`) — [Echo v4](https://echo.labstack.com/) HTTP server. This is the primary server; it handles scanning, media generation, and all DB access natively.
- **string_parser** — the author's own Go package (`github.com/MattThePerson/string_parser`), used by the Go scanner to parse structured metadata out of filenames via config-driven format templates.
- **Python workers** (`py/`) — minimal, self-contained CLI scripts called as subprocesses by Go for two things Go doesn't handle natively: TF-IDF model building/querying and ML-based preview thumbnail extraction. Each script is one-job-only; all paths are passed as explicit CLI flags. The venv lives at `py/.venv`, managed by `uv`.
- **handymatt-media** — the author's own Python library (`py/` dep), used by `py/cmd/generatePreviewThumbs.py` for ML-based frame selection (`extractPreviewThumbs`).
- **Frontend** (`frontend/`) — Svelte 5 + TypeScript + Tailwind v4, Vite-built. The active frontend served by the Go backend. (The old vanilla JS frontend is preserved at `frontend_old/` for reference.)
- **SQLite** — the only data store. Go talks to it directly via `modernc.org/sqlite` (pure-Go, no CGO needed).
- **ffmpeg** — required system dependency; used directly for poster frames, video "teasers", thumbnail spritesheets, and mkv→mp4 remuxing.
- **launcher** (`launcher/`) — a `pystray` tray-icon app that wraps the server process so it can be started/stopped/restarted without a terminal window.

## Architecture

One server, plus "dumb" Python workers for two specific tasks:

1. **Go server** (`go_backend/cmd/app/main.go`, entrypoint built to `bin/CandyPopVideo.exe`) — the only server. Serves the frontend as static files, owns all database reads/writes, runs library scanning, and drives media generation. Exposes route groups: `/media`, `/api`, `/api/query`, `/api/interact`, and `/api/dashboard`. Started directly or via the tray-app launcher.
2. **Python workers** (`py/cmd/`) — one-job-per-script CLI entrypoints: `generateTFIDF.py`, `getSimilarVideos.py`, `getActorInfo.py`, `generatePreviewThumbs.py`. Each script receives everything it needs via explicit CLI flags — no config reading, no app state. Go invokes them via the `internal/pyworker` package (`pyworker.Exec` / `pyworker.ExecOutput`), which discovers `py/` by walking up from the executable dir (or cwd for `go run`), sets `cmd.Dir = py/` so modules resolve as `from lib.X import Y`, and caches the result with `sync.Once`.

Python subprocess calls cover: TF-IDF model building (`cmd.generateTFIDF`, triggered from dashboard and after scan), similar-video recommendations (`cmd.getSimilarVideos`, TF-IDF cosine similarity), actor info scraping (`cmd.getActorInfo`, Babepedia), and ML-based preview thumbnail extraction (`cmd.generatePreviewThumbs`, opt-in only — not included in "all" media type).

## Directory Structure

```
go_backend/             # Go HTTP server (Echo)
    cmd/
        app/main.go     # entrypoint, route registration, static file serving
        worker/main.go  # Go worker stub (not yet implemented)
    internal/
        config/         # config.yaml loader + ConfigStore (RWMutex-protected, hot-reloadable)
        db/             # sqlite access + in-memory video cache
        schemas/        # VideoData, VideoInteractions, query structs
        query/          # search filtering/sorting, catalogue aggregation
        scanner/        # Go-native library scanning: walk, hash, ffprobe, filename parse, DB merge
        mediagen/       # Go-native media generation: teasers, spritesheets (teaser-thumbs + seek-thumbs)
        pyworker/       # Python subprocess helpers: interpreter discovery, Exec, ExecOutput
        routes/         # media / api / query / interact / dashboard route handlers

py/                     # Python workers — minimal, self-contained, called as subprocesses by Go
    cmd/                # one-job entrypoints (run as: python -m cmd.<name> --flag val ...)
        generateTFIDF.py        # build + pickle TF-IDF model from DB
        getSimilarVideos.py     # cosine similarity lookup via pickled matrix
        getActorInfo.py         # Babepedia scraper / actor info cache
        generatePreviewThumbs.py # ML-based poster frame selection (handymatt-media)
    lib/                # shared library modules
        recommender/    # tfidf.py, tfidf_light.py, tfidf_model.py, model_matrix.py, stopwords_eng.py
        actor/          # actor_api.py — Babepedia scraper
        schemas/        # video_data.py — VideoData dataclass
        util/           # db.py (read from sqlite), general.py (pickle save/load)
    pyproject.toml      # uv-managed deps: scikit-learn, scipy, numpy, nltk, requests, bs4, handymatt-media
    .venv/              # created by: cd py && uv sync

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
data/                   # static data files (e.g. English stopwords reference for TF-IDF)
```

## Configuration

Config is stored in `<OS UserConfigDir>/CandyPopVideo/config.yaml` (Windows: `%AppData%\Roaming\CandyPopVideo\config.yaml`, Linux: `~/.config/CandyPopVideo/config.yaml`). The Go binary embeds a default template at `go_backend/internal/config/default_config.yaml` and writes it on first run if the directory doesn't exist. `data/config.yaml` is a reference copy of the same template. Config can be edited via the dashboard's "Edit Config" button, which opens `/config` — a CodeMirror (YAML + vim) editor with live validation and hot-reload.

Storage is split by responsibility:
- **OS app data dir** (`<OS UserConfigDir>/CandyPopVideo/`) — `app.db`, TF-IDF model pickles (`tdidf.pkl`, `tdidf_matrix.pkl`), actor-info cache (`actors/`), `config.yaml` itself.
- **`preview_media_dir`** (user-configured in config.yaml) — generated preview media (teasers, spritesheets, etc.). Changing this field requires a server restart.

Key config.yaml fields:

- `preview_media_dir` — where preview media is written. Cannot be hot-reloaded; requires restart.
- `video_extensions` — which file extensions count as videos when scanning.
- `scene_filename_formats` — an ordered list of pattern templates (most-specific first) used to parse structured metadata (performers, studio, title, year, release date, source id, ...) straight out of filenames. The first pattern that matches a given filename wins.
- `collections` — maps a collection name to one or more absolute folder paths. A path prefixed with `!` is scanned for exclusion only (its contents are ignored even if nested inside an included path).
- `subtitle_folders` — extra folders to search for `.srt` files when serving subtitles.
- `datetime_format` — display format for dates in the frontend.
- `curated_collections` — list of named saved searches shown on the `/curated` page. Each entry has `name`, `description`, and a `query` object whose fields (`actor`, `studio`, `tags`, `sortby`, etc.) map to the standard search filters.

The Go config package (`go_backend/internal/config/config.go`) exposes `ConfigStore` (RWMutex-protected, hot-reloadable) and `NewConfigStore()` (handles first-run bootstrap). Python worker scripts never read config.yaml — the Go server passes all needed paths as explicit CLI flags (`--db-path`, `--model-dir`, `--model-path`, `--actor-info-dir`, `--media-dir`).

## Data Model

Videos are identified by a **content hash**, not by file path or filename — the schema-level comment in `go_backend/internal/schemas/video_interactions.go` and the use of hash as primary key throughout reflects that paths are expected to change (renames, moves, drive reshuffles) while the hash-keyed metadata and interaction history must survive that. Scanning re-uses the existing hash for a path it already knows about and only re-hashes when a file's path can't be matched to an existing record.

SQLite is used unconventionally: rather than normalized columns, each table (`videos`, `interactions`) stores one row per video keyed by `id` (the hash) with a single `data` column holding a JSON blob of the full struct (see `ReadSerializedRowFromTable` / `WriteSerializedRowToTable` in `go_backend/internal/db/db.go`). A `views` table is the one exception — it's appended to as a plain log of `(timestamp, video_hash, duration_sec)` rows rather than serialized. The DB runs in WAL mode for concurrent reads/writes. The Go server also keeps a short-lived in-process cache of the entire deserialized `videos` table (`internal/db/cache.go`) to avoid re-parsing JSON on every request — it's invalidated after a base timeout *and* no further access within an access timeout.

**`VideoData`** (`go_backend/internal/schemas/video_data.go`, mirrored as a Python dataclass in `py/lib/schemas/video_data.py`) — everything derived from the file itself plus parsed/external metadata:
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

**Scanning** (`go_backend/internal/scanner/`) — Go-native. Walks all configured collection folders (`walk.go`), filters by extension and ignore list, computes a stable SHA-256 content hash from three 64 KB chunks of each file (`hash.go`), probes video attributes via ffprobe (`attributes.go`), parses each filename against `scene_filename_formats` using the `string_parser` package (`filename.go`), and merges results into the DB without clobbering manually-edited fields (`merge.go`). Videos no longer found on disk are marked `is_linked: false` rather than deleted, so interaction history survives reconnected drives. Triggered from the dashboard (`POST /api/dashboard/run-scan`) or directly. After a scan completes, Go shells out to `py/cmd/generateTFIDF.py` to rebuild the TF-IDF model.

**Media generation** — split between Go (primary) and Python (ML preview thumbs only):
- **Go** (`go_backend/internal/mediagen/`) — handles teasers (`teaser.go`: N evenly-spaced clips scaled/concatenated via ffmpeg) and spritesheet thumbnail sets (`spritesheet.go`: tiled JPEG sprites + VTT sidecar). Spritesheets use a channel-based goroutine worker pool: a fixed number of workers (typically 3–6) drain a closed work channel of frame indices, each firing a single `ffmpeg -ss` frame-extract. On-demand routes use a semaphore (`chan struct{}` of capacity 3) to cap concurrent HTTP-triggered ffmpeg processes. Batch generation is gated by collection/path/age filters. Triggered from the dashboard (`POST /api/dashboard/generate-media`) or on-demand by `/media/ensure/*` routes.
- **Python** (`py/cmd/generatePreviewThumbs.py`, subprocess call) — ML-based preview thumbnail extraction via `handymatt_media.media_generator.extractPreviewThumbs`. Creates `<media-dir>/0x<hash>/previewthumbs/` with ~10 images at 360 and 1080 resolution. Opt-in only — not included when `media_type` is `"all"` (too slow for bulk runs). Flagged with a "Python" badge in the dashboard UI.

Generated media is cached to `preview_media_dir` keyed by video hash, and only regenerated if missing or forced via `redo` flag.

**Search & recommendations** (`py/lib/recommender/`, `py/cmd/`) — `generateTFIDF.py` builds a TF-IDF model (scikit-learn `TfidfVectorizer` + Snowball stemming, English stopwords in `py/lib/recommender/stopwords_eng.py`) over tokens from each video's metadata and pickles the result (`tdidf.pkl`, `tdidf_matrix.pkl`) to the OS app data dir. `getSimilarVideos.py` loads the lighter matrix-only pickle and computes cosine similarity on demand. Both are invoked as subprocesses by the Go server via `pyworker.Exec`/`pyworker.ExecOutput`.

**Filtering/sorting/catalogue** (`go_backend/internal/query/`) — the Go-native, non-TF-IDF half of search: structural filtering by actor/studio/collection/tags/date ranges/favorites, configurable sort (including a natural-sort-aware title comparator that treats embedded numbers as numbers, see `formatStringForIntComparability`), and catalogue aggregation (grouping videos by actor/studio/collection/tag with counts and "newest video" info for browsing pages).

**Media serving quirks** — non-mp4/webm containers (notably `.mkv`) aren't directly playable in a `<video>` element, so the Go server pipes them through `ffmpeg -c copy -movflags frag_keyframe+empty_moov -f mp4` on the fly rather than transcoding the whole file up front.

## Frontend (old — reference only)

`frontend_old/` is the original vanilla-JS frontend, no longer served. Kept as reference. Structure:

- `pages/<name>/` — one folder per route, each with `page.html`, `script.js`, and `styles.css`.
- `shared/components/` — HTML-string functions injected at load time (homegrown component system).
- `shared/web_components/` — custom elements (`customElements.define`), e.g. search panel and result cards.
- `shared/libraries/` — vendored JS, most notably **PassionPlayer**, a custom `<video>`-based player supporting editable timeline markers/annotations (the backing store for `VideoInteractions.markers`/`dated_markers`).

## Launcher

`launcher/tray_app.py` + `launcher/ProcessManager.py` wrap the server executable in a system tray icon (start/stop/restart, log to a rotating file handler) so the app can run unattended without a visible console. Packaged to a standalone executable via PyInstaller (`make build-launcher` / the `build` target in `tools/Windows.mak` / `tools/Linux.mak`).

## Build & Run

- `cd py && uv sync` — creates `py/.venv` and installs Python worker dependencies.
- `make build-go` — builds the Go server to `bin/CandyPopVideo.exe` (or unsuffixed on Linux).
- `make build-launcher` — packages the tray app to `bin/CandyPopVideoTrayApp.exe` via PyInstaller.
- `make build` — both of the above.
- `tools/run_go.ps1` / equivalent — runs the built Go server.
- Both Makefiles are OS-gated through the root `Makefile`, which includes `tools/Windows.mak` on Windows and `tools/Linux.mak` otherwise.
- Docker is also supported as an alternative to the tray app/native install — see `Dockerfile`; requires mounting `app_data_dir`, the video library paths, and `config.yaml` as volumes.

## Known Gaps / In-Progress Areas

(See `NOTES.md` for the live, unfiltered TODO list.) Notable unfinished or partial pieces as of now:

- Go routes still stubbed (`501 Not Implemented`): `GET /api/query/get/similar-actors/:name`, `GET /api/query/get/similar-studios/:name`, marker get/update.
- TF-IDF-ranked sorting of free-text search results isn't wired up on the Go side yet — the search route filters/sorts structurally but doesn't call the TF-IDF subprocess for `search_string` ranking.
- Performer/studio embeddings (for "similar actor/studio" features) are planned but unimplemented (`py/lib/recommender/similarity.py` has the stub).

## Svelte rewrite

The vanilla-JS frontend (preserved at `frontend_old/` for reference) is fully replaced by `frontend/` — a Svelte 5 + TypeScript + Tailwind v4 project (Vite-built, no SvelteKit). All six pages are functional. Stage 1 of the frontend rewrite is complete.

- **Router** (`src/lib/router/`) — hand-rolled, no third-party package, real URL paths (history mode, not hash routing):
  - `router.svelte.ts` — `routerState` (`$state`-backed current path + search), `navigate(path, { replace? })`, `initRouter()` (wires `popstate` + a delegated `document` click listener that intercepts same-origin `<a>` clicks and routes them client-side, skipping modifier-clicks/`target`/`download`/external links), and `matchRoute`/`matchPattern` (segment-based matching with `:param` support). The `.svelte.ts` suffix is required for top-level rune usage outside a `.svelte` file.
  - `routes.ts` — ordered `{ pattern, component }` table, checked first-match-wins. Routes: `/`, `/search`, `/catalogue`, `/curated`, `/video/:hash`, `/dashboard`, `/config`.
  - `App.svelte` calls `initRouter()` on mount, derives the current match via `matchRoute(routerState.path)`, and renders `<Header />` / the matched page (spreading params as props) / `<Footer />`.
- **Components** (`src/lib/components/`):
  - `Header.svelte` — logo, home/search/catalogue/curated nav links, shuffle/search/dashboard/settings icon buttons, active-link highlighting driven by `routerState.path`.
  - `Footer.svelte` — simple copyright line.
  - `Spinner.svelte` — reusable orange gradient ring animation. Props: `size` (px, default 52) and `bg` (inner-circle colour, default `#060A0A`).
  - `SearchPanel.svelte` — full filter/sort sidebar used by the search page. Syncs all filter state to URL params via `navigate('/search?...')`. Supports: query, actor, studio, collection, include/exclude terms, tags, favourites toggle, sort (12 modes), results-per-page selector.
  - `ConfirmDialog.svelte` — reusable modal confirmation dialog. Props: `message`, `confirmLabel`, `onConfirm`, `onCancel`. Escape key via `$effect`, click-outside dismissal.
  - `cards/DefaultCard.svelte` — the full video card. Poster image with hover sprite-sheet teaser; stats overlay; interactions loaded from `/api/interact/get/:hash` (viewtime, likes, rating, favourite toggle with optimistic UI); four size variants ('small'/'medium'/'large'/'xl').
  - `cards/VideoCard.svelte` — thin wrapper that selects card variant via `settings.cardVariant`.
  - `RenameOverlay.svelte` — F2 modal for renaming a video file. Real-time validation, unmounts player before request, undo bar after success.
- **Types** (`src/lib/types/`):
  - `video.ts` — `VideoData` and `VideoInteractions` TypeScript interfaces.
  - `query.ts` — `SearchQuery` and `CatalogueQuery` interfaces.
- **Stores / utilities** (`src/lib/stores/`, `src/lib/util/`):
  - `settings.svelte.ts` — singleton `settings` persisted to `localStorage`. Fields: `cardVariant`, `cardSize` ('small'|'medium'|'large'|'xl'), `teaserMode` ('sprite'|'video'), `resultsPerPage` (4|8|16|24|36).
  - `configBuffer.svelte.ts` — localStorage-backed buffer for unsaved config edits. Fields: `content` (get/set), `savedAt`, `isDirty` ($derived), `clear()`. Used by the config editor page to survive navigation away before saving.
  - `pager.svelte.ts` — `createPager<T>(source, batchSize)` factory. Exposes `visible`, `hasMore`, `loadMore()`, `reset()`. Used by the home page.
- **Pages** (`src/pages/<name>/Page.svelte`) — all fully implemented:
  - `home` — spotlight video (full-width 21:9 `VideoCard`) + paginated similar-video grid.
  - `search` — URL-driven state (all filter/sort/page params live in `?q=&actor=&page=...`). `$effect` on `routerState.search` fires the search; result grid uses `VideoCard`; `PageNav` handles pagination.
  - `catalogue` — tab bar (actors / studios / collections / tags), sort modes (alphabetic / count / newest), min-video threshold slider, alphabetic grouping with letter-nav buttons. All tab/sort state in URL params. `CatalogueItem` sub-component per row.
  - `curated` — list view (`/curated`): cards for each named saved-search defined in `config.yaml`. Detail view (`/curated?c=<name>`): runs the collection's query via `POST /api/query/search-videos`, shows video grid + `PageNav`. Back button returns to list view.
  - `video` — resolves `random` sentinel, fetches `VideoData` + `VideoInteractions` in parallel, renders `VideoPlayer` / `VideoDetails` / `RelatedVideos` / `SimilarVideos`. F2 opens `RenameOverlay`.
  - `dashboard` — scan controls, media generation controls, TF-IDF rebuild, "Edit Config" button. Real-time job log via SSE.
  - `config` — CodeMirror 6 editor (YAML + vim motions + one-dark theme) for editing `config.yaml` in-browser. Saves via `POST /api/config/save`, shows validation errors/warnings, flags `preview_media_dir` changes as requiring restart. Unsaved edits buffered in `configBuffer` store (survives navigation). Discard and Restore Defaults buttons with `ConfirmDialog`.
- Colors/fonts: `src/app.css` defines a global dark `body` background (`#060A0A`), a Tailwind v4 `@theme` block with `--color-*` tokens, and `@font-face` rules for `Jaro-Regular.ttf` and the Inter variable font.
- The Go server serves `frontend/dist/assets` and `favicon.svg` directly, then falls back to `frontend/dist/index.html` for any other GET so client-side routes survive a hard refresh.
- The Vite dev server proxies `/api`, `/media`, and `/static` to `http://localhost:8010` (the Go backend port) so API calls work during `npm run dev` without CORS issues.
- Building: `npm install` / `npm run build` manually inside `frontend/` (no `make build-frontend` target yet).
