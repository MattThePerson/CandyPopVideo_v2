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
- [ ] **Home** — spotlight video, recent videos, in-progress (partially done: video cards, similar videos loading)
- [ ] **Search** — search bar, filters panel, result grid (placeholder)
- [ ] **Catalogue** — browse by actor/studio/collection/tag with counts (placeholder)
- [ ] **Curated** — curated collections list + detail view (placeholder)
- [ ] **Video** — player, metadata panel, markers, similar videos, interactions (placeholder)
- [ ] **Dashboard** — library management UI (stub; will expand in Stage 3)

### Shared Components
- [ ] **VideoCard** — tile for video grids (in progress)
- [ ] **Search panel** — filters sidebar/drawer
- [ ] **Video player** — PassionPlayer
- [ ] **Markers / timeline** — editable annotation layer on the player
- [ ] **Catalogue cards** — actor, studio, collection, tag tiles

---

## Stage 2 — Full Go Backend

**Goal:** Eliminate the Python dependency entirely. All functionality currently in `python_src/` moves to Go.

> **Breaking change:** hashing algorithm will be reimplemented in Go, producing different hashes. A one-time DB migration will be required.

### Scanning
- [ ] Filesystem walker (collection folders, extension filter, ignore-list)
- [ ] Filename parser (scene_filename_formats pattern matching)
- [ ] JSON sidecar loader
- [ ] File hasher (Go reimplementation of `handymatt-media` algorithm)
- [ ] DB merge logic (preserve interactions on re-scan, mark missing as `is_linked: false`)

### Media Generation
- [ ] Poster frame extraction (ffmpeg)
- [ ] Teaser clip generation (ffmpeg)
- [ ] Thumbnail spritesheet generation — teaser thumbs + seek thumbs (ffmpeg)
- [ ] GIF generation (new; see Stage 4)
- [ ] MKV → MP4 remux (already in Go, verify parity)
- [ ] On-demand `/media/ensure/*` routes (replace subprocess calls)

### Search & Recommendations
- [ ] TF-IDF model build + pickle replacement (Go-native or embedded model)
- [ ] Free-text search ranking via TF-IDF cosine similarity
- [ ] Similar-videos lookup
- [ ] Actor/studio profile vectors (average of member video vectors; see Stage 4)

### Misc Python Routes
- [ ] Actor info lookup (currently `worker_scripts/`)
- [ ] Port any remaining FastAPI routes not yet in Go

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
- [ ] Scan trigger + live progress feed (SSE or polling)
- [ ] Media generation trigger + status
- [ ] TF-IDF rebuild trigger
- [ ] Library health view (`is_linked: false` videos, missing media)
- [ ] DB stats / storage usage

---

## Stage 4 — General Improvements

**Goal:** Feature additions and polish on top of the stable Stages 1–3 base.

- [ ] **Video interactions** — improve UX for ratings, markers, comments, dated markers
- [ ] **Site-wide content filters** — persistent filter (e.g. single collection/studio) applied globally across all pages
- [ ] **GIF generation + viewing** — generate animated GIF previews; display in UI
- [ ] **Catalogue improvements** — better sorting, faceted browsing, infinite scroll
- [ ] **Actor/studio TF-IDF profiles** — average video vectors → "similar actors/studios" feature
- [ ] **Alternative/advanced search** — synonym expansion, semantic model (may reintroduce a narrow Python dependency or use an embedded model)
