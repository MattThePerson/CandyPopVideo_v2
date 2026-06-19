# Progress

## Stage 1 — Full Svelte Frontend

**Goal:** Replace `frontend_old/` (vanilla JS) entirely with `frontend/` (Svelte 5 + TS + Tailwind v4).

### Infrastructure
- [x] Vite + Svelte 5 + Tailwind v4 project scaffold
- [x] Hand-rolled client-side router (history mode, `:param` support)
- [x] Header + Footer components
- [x] Route table (home, search, catalogue, curated, video, dashboard)
- [x] Go server serving `frontend/dist` + SPA fallback

### Pages
- [x] **Home** — spotlight video, recent videos, in-progress (partially done: video cards, similar videos loading)
- [x] **Search** — search bar, filters panel, result grid (placeholder)
- [x] **Catalogue** — browse by actor/studio/collection/tag with counts (placeholder)
- [x] **Curated** — curated collections list + detail view (placeholder)
- [x] **Video** — player, metadata panel, markers, similar videos, interactions (placeholder)
- [ ] **Dashboard** — library management UI (stub; will expand in Stage 3)

### Shared Components
- [x] **VideoCard** — tile for video grids (in progress)
- [x] **Search panel** — filters sidebar/drawer
- [x] **Video player** — PassionPlayer
- [ ] **Markers / timeline** — editable annotation layer on the player
- [x] **Catalogue cards** — actor, studio, collection, tag tiles

---

## Stage 2 — Go Worker + Dashboard

**Goal:** Move scanning and media generation to Go, expose them via a first-class dashboard UI. Python stays for TF-IDF/recommendations (latency is acceptable there) and for ML-based features (nudenet thumbnail selection, actor info scraping). Broken into three sub-stages.

> **Breaking change:** hashing algorithm will be reimplemented in Go (ffmpeg frame extraction + xxHash, replacing the OpenCV-based approach in `handymatt_media`). This produces different hashes — a one-time DB migration is required before Stage 2b goes live.

**Python stays for:**
- TF-IDF model build, similar-videos, search ranking (`python_src/recommender/`) — subprocess calls remain
- ML-based preview thumbnail selection (`handymatt_media.extractPreviewThumbs` uses nudenet) — subprocess call remains
- Actor info scraping (Babepedia + nudenet image filtering) — subprocess call remains

---

### Stage 2a — Dashboard UI

**Goal:** Full Svelte dashboard page; Go provides SSE/polling skeleton endpoints (stub data initially, filled in as 2b/2c land).

- [ ] Dashboard page layout (library stats panel, scan controls, media-gen controls, TF-IDF rebuild controls)
- [ ] SSE endpoint for job progress (Go stub: streams placeholder events)
- [ ] Library health view — unlinked videos, missing media by type, DB stats
- [ ] Scan trigger UI (options: reparse filenames, reread JSON, rehash)
- [ ] Media generation trigger UI (type selector, path filter, redo toggle)
- [ ] TF-IDF rebuild trigger UI (shells out to Python worker, as before)
- [ ] Job log / output panel (streams SSE lines while a job runs)

---

### Stage 2b — Go Scanner

**Goal:** Full library scan implemented in Go, wired to the dashboard scan trigger.

- [ ] Filesystem walker (collection folders, extension filter, ignore hidden dirs/dot-folders)
<!--- [ ] NTFS ADS read/write (`candypop-video-hash` stream — Windows `CreateFileW` `:streamname` trick)-->
- [ ] Video hashing — ffmpeg frame extraction + xxHash (new algo; DB migration required)
- [ ] Video attribute extraction — `ffprobe` JSON output (duration, fps, resolution, bitrate, filesize)
- [ ] Filename parser — use the new `go-string-parser` package (developed separately)
- [ ] JSON sidecar loader — per-video / per-folder metadata merge
- [ ] Movie/series title extraction — pure string logic (Scene N, Part N, Vol., Season, ` - ` delimiter)
- [ ] Path-based tag extraction + sort by frequency across collection
- [ ] DB merge logic — preserve interactions on re-scan, mark missing as `is_linked: false`
- [ ] SSE progress streaming during scan (wired to dashboard job log)

---

### Stage 2c — Go Media Generator

**Goal:** Go handles all ffmpeg-based media generation; on-demand routes no longer shell out to Python for these types.

- [ ] Poster frame — ffmpeg at 20% duration
- [ ] Teaser clip — duration-based clip-count formula, N×1.3s clips spread 0–98%, ffmpeg concat demuxer
- [ ] Teaser thumbs small — ffmpeg `fps+scale+tile`, 16 frames @ 300px, VTT file
- [ ] Seek thumbs — ffmpeg `fps+scale+tile`, 400 frames @ 300px, VTT file
- [ ] Media status checks — file-existence helpers for all Go-generated media types
- [ ] Batch media generation with filter/limit/redo options (wired to dashboard)
- [ ] On-demand `/media/ensure/*` routes updated to use Go generators (except ML preview thumbs)
- [ ] ML preview thumbs remain as Python subprocess (`handymatt_media.extractPreviewThumbs` / nudenet)

---

## Stage 3 — Go Refactor

**Goal:** Clean up the backend architecture and add first-class multi-profile support.

### Database
- [ ] Replace JSON-blob schema with normalized SQLite columns/tables
- [ ] Migration from blob schema (include hash migration from Stage 2)
- [ ] Proper indices for common query patterns

### Profiles
- [ ] Profile entity (name, config overrides, per-profile interaction history)
- [ ] Profile-aware DB reads/writes throughout
- [ ] Frontend: profile switcher in Header
- [ ] Frontend: per-profile settings page

### Dashboard (frontend + backend)
- [ ] Dashboard enhancements post-Stage-2 (profile-aware stats, per-profile media status)

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
