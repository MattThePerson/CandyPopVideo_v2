# Progress

## Stage 1 — Full Svelte Frontend ✓ COMPLETE

**Goal:** Replace `frontend_old/` (vanilla JS) entirely with `frontend/` (Svelte 5 + TS + Tailwind v4).

### Infrastructure
- [x] Vite + Svelte 5 + Tailwind v4 project scaffold
- [x] Hand-rolled client-side router (history mode, `:param` support, URL search params)
- [x] Header + Footer components
- [x] Route table (home, search, catalogue, curated, video, dashboard, config)
- [x] Go server serving `frontend/dist` + SPA fallback

### Pages
- [x] **Home** — spotlight video + paginated similar-video grid
- [x] **Search** — URL-driven state; SearchPanel filters; paginated result grid (PageNav)
- [x] **Catalogue** — tabs (actors/studios/collections/tags); sort modes; alphabetic grouping + letter nav
- [x] **Curated** — list view of named saved-searches from config.yaml; detail view runs the query + paginates
- [x] **Video** — player, metadata panel, related/similar videos, interactions, F2 rename
- [x] **Dashboard** — scan controls, media gen controls, TF-IDF rebuild, SSE job log, Edit Config button
- [x] **Config** — CodeMirror YAML editor (vim motions), validation, hot-reload, unsaved-change buffer

### Shared Components
- [x] **VideoCard / DefaultCard** — tile for video grids, sprite-sheet hover teaser, interactions
- [x] **SearchPanel** — full filter/sort sidebar with 12 sort modes, all filters sync to URL
- [x] **Video player** — PassionPlayer
- [x] **Catalogue cards** — CatalogueItem (actor/studio/collection/tag rows with counts)
- [x] **PageNav** — smart pagination widget (used by search + curated)
- [x] **ConfirmDialog** — reusable modal confirmation (used by config editor)
- [x] **RenameOverlay** — F2 rename modal with real-time validation and undo bar
- [ ] **Markers / timeline** — editable annotation layer on the player (deferred to Stage 4)

---

## Stage 2 — Go Worker + Dashboard

**Goal:** Move scanning and media generation to Go, expose them via a first-class dashboard UI. Python stays for TF-IDF/recommendations (latency is acceptable there) and for ML-based features (nudenet thumbnail selection, actor info scraping). Broken into three sub-stages.

> **Breaking change:** hashing algorithm will be reimplemented in Go (ffmpeg frame extraction + xxHash, replacing the OpenCV-based approach in `handymatt_media`). This produces different hashes — a one-time DB migration is required before Stage 2b goes live.

**Python stays for:**
- TF-IDF model build, similar-videos, search ranking (`python_src/recommender/`) — subprocess calls remain
- ML-based preview thumbnail selection (`handymatt_media.extractPreviewThumbs` uses nudenet) — subprocess call remains
- Actor info scraping (Babepedia + nudenet image filtering) — subprocess call remains

---

### Stage 2a — Dashboard UI ✓

**Goal:** Full Svelte dashboard page; Go provides SSE/polling skeleton endpoints (stub data initially, filled in as 2b/2c land).

- [x] Dashboard page layout (library stats panel, scan controls, media-gen controls, TF-IDF rebuild controls)
- [x] SSE endpoint for job progress (Go stub: streams placeholder events)
- [x] Library health view — unlinked videos, missing media by type, DB stats
- [x] Scan trigger UI (options: reparse filenames, reread JSON, rehash)
- [x] Media generation trigger UI (type selector, path filter, redo toggle)
- [x] TF-IDF rebuild trigger UI (shells out to Python worker, as before)
- [x] Job log / output panel (streams SSE lines while a job runs)

---

### Stage 2b — Go Scanner ✓

**Goal:** Full library scan implemented in Go, wired to the dashboard scan trigger.

- [x] Filesystem walker (collection folders, extension filter, ignore hidden dirs/dot-folders)
- [x] Video hashing — SHA-256 of three 64 KB chunks at offsets 0 / size/2 / size-chunk (interoperable with `handymatt` Go projects; no DB migration needed, dev DB was wiped)
- [x] Video attribute extraction — `ffprobe` JSON output (duration, fps, resolution, bitrate, filesize)
- [x] Filename parser — `github.com/MattThePerson/string_parser v0.1.3`; `#Tag` tokens extracted from stem before parsing
- [x] Path-based tag extraction + sort by frequency across collection (all three tag sources: filename, path, JSON)
- [x] DB merge logic — preserve interactions on re-scan, mark missing as `is_linked: false`
- [x] SSE progress streaming during scan (wired to dashboard job log)
- [ ] JSON sidecar loader — deferred to later stage

---

### Stage 2c — Go Media Generator ✓

**Goal:** Go handles all ffmpeg-based media generation; on-demand routes no longer shell out to Python for these types.

- [x] Poster frame — ffmpeg at 20% duration
- [x] Teaser clip — duration-based clip-count formula, N×1.3s clips spread 0–98%, ffmpeg concat demuxer
- [x] Teaser thumbs small — ffmpeg `fps+scale+tile`, 16 frames @ 300px, VTT file
- [x] Seek thumbs — ffmpeg `fps+scale+tile`, 400 frames @ 300px, VTT file
- [x] Media status checks — file-existence helpers for all Go-generated media types
- [x] Batch media generation with filter/limit/redo options (wired to dashboard)
- [x] On-demand `/media/ensure/*` routes updated to use Go generators (except ML preview thumbs)
- [x] ML preview thumbs remain as Python subprocess (`handymatt_media.extractPreviewThumbs` / nudenet)

---

## Stage 3 — Go Refactor

**Goal:** Clean up the backend architecture and add first-class multi-profile support.

### Database
- [ ] Replace JSON-blob schema with normalized SQLite columns/tables
- [ ] Migration from blob schema (include hash migration from Stage 2)
- [ ] Proper indices for common query patterns

---

## Stage 4 — General Improvements

**Goal:** Feature additions and polish on top of the stable Stages 1–3 base.

- [ ] **Video interactions** — improve UX for ratings, markers, comments, dated markers
- [ ] **Site-wide content filters** — persistent filter (e.g. single collection/studio) applied globally across all pages
- [ ] **GIF generation + viewing** — generate animated GIF previews; display in UI
- [ ] **Catalogue improvements** — better sorting, faceted browsing, infinite scroll
- [ ] **Actor/studio TF-IDF profiles** — average video vectors → "similar actors/studios" feature
- [ ] **Alternative/advanced search** — synonym expansion, semantic model (may reintroduce a narrow Python dependency or use an embedded model)
- [ ] **Video renaming** — along with reparsing the filename data
- [ ] **Video tags** — tagging system which is included in search stuff
