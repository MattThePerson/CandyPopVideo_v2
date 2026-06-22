# go_backend/CLAUDE.md

## Package Layout

```
cmd/app/main.go         — entrypoint: Echo setup, middleware, route-group wiring, static serving
cmd/worker/main.go      — stub, not yet implemented
internal/
  config/               — Config struct, ConfigStore (RWMutex + hot-reload), embeds default_config.yaml
  db/                   — generic JSON-row SQLite helpers + in-memory video cache
  schemas/              — VideoData, VideoInteractions, SearchQuery, CatalogueQuery
  routes/               — one file per route group; shared helpers in 0_routes_helpers.go
  scanner/              — walk → hash → ffprobe → filename parse → DB merge
  query/                — FilterAndSortVideos, GetCatalogue (pure Go, no DB I/O)
  mediagen/             — teaser clips and spritesheet generation via ffmpeg
  pyworker/             — subprocess executor for all Python workers
```

Module name: `cpv_backend`. Go 1.24.4.

---

## Entrypoint — main.go

```
cmd/app/main.go
```

Flags: `-dev` (NoCacheMiddleware for .html/.js/.css), `-port` (default 8010).

Startup sequence:
1. `config.NewConfigStore()` — reads/bootstraps config.yaml, `log.Fatal` on failure.
2. `db.InitDB(cfg.DBPath)` — creates tables if absent, WAL mode.
3. Echo setup: logger (`${method} ${uri} ${status} ${latency_human}`), recover middleware, optional NoCacheMiddleware.
4. Route group wiring — each group receives only the config values it needs (no global config):

```go
routes.IncludeMediaRoutes(    e.Group("/media"),         cfg.DBPath, cfg.PreviewMediaDir, cfg.SubtitleFolders)
routes.IncludeApiRoutes(      e.Group("/api"),           cfg.DBPath, cfg.ActorInfoDir, store)
routes.IncludeQueryRoutes(    e.Group("/api/query"),     cfg.DBPath, cfg.TfidfMatrixPath)
routes.IncludeInteractRoutes( e.Group("/api/interact"),  cfg.DBPath)
routes.IncludeDashboardRoutes(e.Group("/api/dashboard"), store)
routes.IncludeRenameRoutes(   e.Group("/api"),           store)
routes.IncludeConfigRoutes(   e.Group("/api"),           store)
```

5. Static serving: `frontend/dist/` assets, `/static/preview-media` → `cfg.PreviewMediaDir/preview`, `/static/actor-store` → `cfg.ActorInfoDir`.
6. SPA catch-all: all unmatched `GET /*` → `frontend/dist/index.html`.

---

## Route Handler Pattern

Route registration uses a thin closure that calls a named `ECHO_` function:

```go
// registration (in IncludeXxxRoutes)
g.GET("/get/video-data/:hash", func(c echo.Context) error {
    return ECHO_get_video_data(c, db_path)
})

// handler
func ECHO_get_video_data(c echo.Context, db_path string) error {
    hash := c.Param("hash")
    vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", hash)
    if err != nil {
        return handleServerError(c, 500, "Unable to read from database", err)
    }
    return c.JSON(200, vd)
}
```

Rules:
- All handlers return `error` (Echo convention).
- Handler function names are `ECHO_verb_noun` — e.g. `ECHO_get_poster`, `ECHO_dashboard_stats`.
- Route-registration functions are `IncludeXxxRoutes(group *echo.Group, ...)`.
- Dependencies are passed as parameters. No global variables.
- The `ConfigStore` is passed to route groups that need hot-reload or multiple config values; individual values (`db_path string`, etc.) are passed to groups that only need a snapshot.
- Call `cfg := store.Current()` inside the closure (not outside) so each request gets the current snapshot. `store` is only captured by groups that need live reload; inside those groups, `store.Current()` is called per-request or per-handler.

---

## Error Handling

All server errors go through `handleServerError` (`0_routes_helpers.go:23`):

```go
func handleServerError(c echo.Context, status int, msg string, err error) error {
    log.Printf("🚨🚨 ERROR 🚨🚨: [%s] %s: %s", c.Path(), msg, err.Error())
    return c.String(status, msg+": "+err.Error())
}
```

Standard patterns:

| Situation | Status | Call |
|---|---|---|
| DB read failure | 500 | `handleServerError(c, 500, "Unable to read from database", err)` |
| DB read for cached data | 500 | `handleServerError(c, 500, "Unable to read table", err)` |
| Bad JSON request body | 400 | `c.JSON(400, map[string]string{"error": "..."})` |
| Job already running | 409 | `c.JSON(409, map[string]string{"error": "A job is already running"})` |
| Python subprocess failed | 500 | `handleServerError(c, 500, "Python subprocess failed", err)` |
| Rename: file op failed | 409 | return after OS error, before DB is touched |
| Rename: DB write failed | 500 | revert the file rename first; if that also fails → `"critical_failure"` |
| No content to return | 204 | `c.NoContent(204)` (e.g. subtitle not found) |

Never pass raw unguarded errors directly to `c.JSON` — always go through `handleServerError` for 500s.

---

## Config

**`Config` struct** (`config/config.go:34`) — fields populated from YAML:

```
PreviewMediaDir, DatetimeFormats, SubtitleFolders, Collections,
VideoExtensions, SceneFilenameFormats, CuratedCollections
```

Derived at parse time via `deriveFields()` (never written to YAML):

```
AppDataDir      — OS UserConfigDir/CandyPopVideo/
DBPath          — AppDataDir/app.db
TfidfModelPath  — AppDataDir/tdidf.pkl
TfidfMatrixPath — AppDataDir/tdidf_matrix.pkl
ActorInfoDir    — AppDataDir/actors/
```

**`ConfigStore`** — thread-safe wrapper with `sync.RWMutex`:
- `store.Current()` — read lock, returns a value-copy snapshot. Safe to call from any goroutine.
- `store.WriteAndReload(yaml []byte) (requiresRestart bool, err)` — write lock, atomically updates. Returns `true` if `PreviewMediaDir` changed (requires server restart; static route was already set up).
- `store.RawYAML()` — reads raw bytes from disk for the config editor endpoint.

`NewConfigStore()` handles first-run (creates dir + writes `default_config.yaml` via `//go:embed`).

**Collections config format**: `{ "Name": ["/path/a", "!/path/excluded"] }`. A `!`-prefixed path is walked for exclusion only.

---

## Database

SQLite, WAL mode. Three tables, created by `db.InitDB()`:

```sql
CREATE TABLE videos       (id TEXT PRIMARY KEY, date_added TEXT, path TEXT NOT NULL DEFAULT '', is_linked INTEGER NOT NULL DEFAULT 1, data TEXT)
CREATE TABLE interactions (id TEXT PRIMARY KEY, data TEXT)
CREATE TABLE views        (timestamp TEXT, video_hash TEXT, duration_sec REAL)
```

`videos` has three shadow columns (`date_added`, `path`, `is_linked`) that are dual-written alongside the JSON blob for SQL-level queries. The blob remains authoritative for API responses. `interactions` stores one JSON blob per row. `views` is an append-only log.

### Generic row helpers (`db/db.go`)

```go
// Read one row
vd, err := db.ReadSerializedRowFromTable[schemas.VideoData](db_path, "videos", hash)

// Read all rows as map[id]struct (all rows, regardless of is_linked)
mp, err := db.ReadSerializedMapFromTable[schemas.VideoData](db_path, "videos")

// Write one row for non-videos tables (INSERT OR REPLACE, no shadow columns)
err = db.WriteSerializedRowToTable(db_path, "interactions", hash, inter)

// Append a row with arbitrary columns (used for views table)
err = db.InsertDataIntoTable(db_path, "views", map[string]any{...})
```

### Videos-specific helpers (`db/db.go`)

```go
// Write a video row — use instead of WriteSerializedRowToTable for the videos table.
// Always sets is_linked=1 and keeps shadow columns (path, date_added) in sync with the blob.
err = db.WriteVideoRow(db_path, hash, vd)

// Mark all videos is_linked=0 in one SQL UPDATE. Called at start of a full scan.
err = db.SetAllUnlinked(db_path)

// Return only linked videos (WHERE is_linked=1) as map[hash]VideoData.
mp, err := db.ReadLinkedVideosMap(db_path)

// Return (linked, unlinked) counts via GROUP BY. Used by dashboard stats.
linked, unlinked, err := db.CountVideosByLinkedStatus(db_path)
```

Each call opens and closes its own connection. No connection pool — this is intentional; WAL mode handles concurrency.

### Cache (`db/cache.go`)

`db.GetCachedVideos(db_path, base_ttl_s, access_ttl_s)` returns `map[hash]VideoData` of **linked-only** entries (via `ReadLinkedVideosMap` — SQL does the filtering). Cache is valid until both the base TTL (15 s) AND the access TTL (3 s) have expired simultaneously. Invalidated explicitly by `db.InvalidateCache()` after any write that changes the video set.

`db.GetCachedInteractions(db_path, base_ttl_s, access_ttl_s)` — same TTL semantics, independent mutex. Returns `map[hash]VideoInteractions`. Invalidated by `db.InvalidateInteractionsCache()` after any interaction write. Used by the search route instead of a per-request DB read.

Always call `db.InvalidateCache()` after writing to the `videos` table so the next request re-reads from SQLite.

---

## Schemas

### `VideoData` (`schemas/video_data.go`)

Content-addressed by `Hash` (12-char hex SHA-256 prefix). Whether a video is linked is tracked via the SQL `is_linked` column — it is not a field on the struct. Unlinked records stay in the DB so interaction history survives reconnected drives.

Key timestamps (both set once at first scan, never overwritten on re-scan):
- `DateAdded` — `time.Now()` at first scan, ms precision (`"2006-01-02 15:04:05.000"`). Also written to the SQL `date_added` shadow column.
- `DateDownloaded` — file mtime via `os.Stat().ModTime()`, second precision (`"2006-01-02 15:04:05"`).

Field sources:
- **ffprobe**: `Duration`, `DurationSeconds`, `FPS`, `Resolution`, `Bitrate`, `FilesizeMB`
- **filename parser**: `Title`, `SceneTitle`, `SceneNumber`, `MovieTitle`, `MovieSeries`, `Studio`, `Line`, `DateReleased`, `Description`, `DVDCode`, `SourceID`, `Actors`, `PrimaryActors`, `SecondaryActors`, `TagsFromFilename`
- **path traversal**: `TagsFromPath`, `Collection`, `ParentDir`, `PathRelative`
- **JSON sidecar**: `TagsFromJSON`, anything that maps into `Metadata map[string]any`
- `Tags` is the deduplicated union of all three `TagsFrom*` slices.

### `VideoInteractions` (`schemas/video_interactions.go`)

Same hash key, stored in `interactions` table. Fields:
- `IsFavourite bool`, `FavouritedDate string`
- `Viewtime float64` (cumulative seconds), `LastViewed string`
- `Likes int`
- `Rating string` (`"C"` through `"S+"`) + `RatingScore int` (0–7) for numeric sorting
- `Markers [][3]any` — `(video_time, color, tag)`
- `DatedMarkers [][2]any` — `(video_time, datetime)`
- `Comments [][2]string` — `(comment, datetime)`

Rating scores: `C=0, C+=1, B=2, B+=3, A=4, A+=5, S=6, S+=7`.

### `SearchQuery` / `CatalogueQuery` (`schemas/queries.go`)

Request bodies for `/api/query/*`. Bind with `c.Bind(&q)`. All filter fields are optional. Key `SearchQuery` fields: `Actor`, `Studio`, `Collection`, `Tags []string`, `IncludeTerms []string`, `ExcludeTerms []string`, `OnlyFavourites string`, `SortBy`, `Limit int`, `StartFrom int`, `DateAddedFrom/To`, `DateReleasedFrom/To`.

---

## Query — FilterAndSortVideos (`query/search.go`)

Takes `[]VideoData`, `SearchQuery`, and `map[hash]VideoInteractions`. Pure function, no DB calls. Returns `FilterAndSortResult{SearchResults, FilteredCount, TimeTakenMS}`.

Filter order: favourites → actor (comma-separated AND) → studio/line → collection → date ranges → include/exclude path terms → tags.

Sort options via `SortBy` field (format: `"<field>_asc"` / `"<field>_desc"`):
- Default (empty `SortBy`): descending `DateAdded`
- **OPTION 2 — interaction fields**: `"viewtime"`, `"last_viewed"`, `"favourited_date"`, `"popularity"`. Videos without interactions are dropped from results.
- **OPTION 3 — direct struct sort** (`handleSortByDirectFields`): `date_added`, `date_downloaded`, `date_released`, `title`, `filename`, `path`, `duration`, `bitrate`, `resolution`. Uses `slices.SortFunc` directly on struct fields — no JSON round-trip.
- **OPTION 4 — JSON round-trip fallback** (`handleSortByVideoData`): any other field name. Works by marshal→map→sort→unmarshal (`structsToMaps` / `mapsToStructs`); field name must match the JSON tag exactly.
- **Random**: `"random-<seed>"` — deterministic seeded shuffle.
- `popularity` score = `viewtime/60 + likes*2 + isFavourite*2 + comments*3 + markers + datedMarkers*5 + ratingScore*2`

---

## Scanner (`scanner/`)

`scanner.ScanLibraries(cfg, opts, emit)` — `emit func(string)` is the SSE log sink.

Pipeline per file:
1. **walk** (`walk.go`) — `collectVideoFiles()` traverses all collection roots, filters by extension, applies `!`-excluded paths and optional `PathFilter` substring.
2. **resolve** (`scanner.go:resolveVideo`) — reuse existing hash from `pathToHash` lookup (by path) or re-hash. Detects renames by finding the hash in the DB with a different path.
3. **ffprobe** (`attributes.go`) — runs on new files or when `opts.RedoAttributes=true`. Populates `Duration`, `FPS`, `Resolution`, `Bitrate`, `FilesizeMB`.
4. **filename parse** (`filename.go`) — on new files or when `opts.ReparseFilenames=true`:
   - `ExtractTags(stem)` — scans right-to-left for `#Word` tokens; returns tags + cleaned stem.
   - `ParseFilename(input, formats)` — tries each `scene_filename_formats` pattern (first match wins) via `string_parser`.
   - `PopulateFromParseResult(vd, parsed)` — maps result map to struct fields.
5. **path tags** (`filename.go:ExtractPathTags`) — always re-derived; directory names excluding already-captured actors/studio/line.
6. **frequency sort** (`merge.go:SortTagsByFrequency`) — sorts each video's tags by how common they are across the whole loaded set (most common first).
7. **merge + save** (`merge.go:MergeAndSave`) — for a full scan, calls `SetAllUnlinked` first (one SQL UPDATE); then for each scanned video calls `WriteVideoRow` (INSERT OR REPLACE, sets `is_linked=1`). Existing `DateAdded`, `DateDownloaded`, `Description`, and `Metadata` are preserved from the DB record. Unlinked records are left untouched with `is_linked=0`.
8. **TF-IDF rebuild** — shells out to `py/cmd/generateTFIDF.py` after every scan.

**Hashing** (`hash.go`): reads three 64 KB chunks (offset 0, size/2, size−64KB) through a single `crypto/sha256` hasher. Returns first 12 hex chars. Stable across renames; fast on large files.

`ScanOptions`: `ReparseFilenames`, `RereadJSON`, `RedoAttributes`, `Rehash`, `PathFilter`. Bound from dashboard POST body.

---

## Media Generation (`mediagen/`)

All output goes to `<preview_media_dir>/preview/0x<hash>/`. Skipped if file already exists unless `redo=true`.

**Teasers** (`teaser.go`): N evenly-spaced clips extracted and concatenated via ffmpeg into `teaser_small.mp4`.

**Spritesheets** (`spritesheet.go`): channel-based goroutine worker pool drains a closed frame-index channel. WaitGroup waits for all extractions before tiling. Outputs `teaser_thumbs_small.jpg` (teaser frames) and `seekthumbs.jpg` + `seekthumbs.vtt` (full-video seek thumbnails).

**Batch** (`batch.go`): `BatchGenerate(cfg, opts, emit)`. `GenerateMediaOptions` controls `MediaType` (`"teaser"`, `"spritesheet"`, `"preview-thumbs"`, `"all"`), collection/path filter, `Redo bool`. Preview thumbs (ML-based) are **not** included in `"all"` — must be requested explicitly.

**On-demand** (`media_routes.go`): a semaphore of size 3 (`chan struct{}`) caps concurrent ffmpeg processes triggered by `/media/ensure/*` hover events.

**MKV streaming** (`media_routes.go`): non-mp4/webm files are piped through `ffmpeg -c copy -movflags frag_keyframe+empty_moov -f mp4` on the fly — no transcode, just remux.

---

## Python Workers (`pyworker/`)

`pyworker.Root()` finds the `py/` directory by walking up from both the executable dir and cwd, looking for `py/.venv`. Result cached via `sync.Once`. `log.Fatal` if not found.

```go
// Fire-and-forget — returns elapsed seconds
tt, err := pyworker.Exec("-m", "cmd.generateTFIDF", "--db-path", cfg.DBPath, "--model-dir", cfg.AppDataDir)

// Capture JSON output
data, err := pyworker.ExecOutput[map[string]any]("-m", "cmd.getActorInfo", "--name", name, "--actor-info-dir", actorInfoDir)
```

`ExecOutput` unmarshals combined stdout as JSON. On error, stdout is logged. Scripts never read config.yaml — all paths come in as explicit CLI flags.

Workers: `cmd.generateTFIDF`, `cmd.getSimilarVideos`, `cmd.getActorInfo`, `cmd.generatePreviewThumbs`.

---

## SSE Job Broker (`routes/dashboard_routes.go`)

`dashBroker` is a package-level `*jobBroker` (single global — only one long-running job at a time).

```go
type jobBroker struct {
    mu      sync.Mutex
    running bool
    log     []string           // historical lines for late subscribers
    subs    map[chan string]struct{}
}
```

- `broker.start(fn)` — returns `false` (409) if a job is already running; otherwise launches `fn` in a goroutine, emits `"\x00DONE"` when finished.
- `broker.subscribe()` — returns a snapshot of historical log lines + a buffered channel (cap 256). New subscribers immediately receive all prior lines.
- `broker.emit(line)` — appends to log, non-blocking send to all subscriber channels (`select { case ch <- line: default: }`).
- SSE stream handler (`ECHO_dashboard_job_stream`) — sets SSE headers, replays historical lines, then blocks on `ctx.Done()` or channel. `"\x00DONE"` emits an SSE `event: done` frame.
- Clearing `b.log = nil` on `start()` ensures subscribers to the new job don't see lines from the previous run.

---

## Concurrency Summary

| Resource | Mechanism | Location |
|---|---|---|
| Config | `sync.RWMutex` in `ConfigStore` | `config/config.go` |
| Video cache | `sync.Mutex cacheMutex` | `db/cache.go` |
| Job broker state | `sync.Mutex` in `jobBroker` | `dashboard_routes.go` |
| Spritesheet workers | channel + `sync.WaitGroup` | `mediagen/spritesheet.go` |
| On-demand media gen | semaphore (`chan struct{}{3}`) | `media_routes.go` |
| pyworker root path | `sync.Once` | `pyworker/pyworker.go` |

---

## Naming Conventions

| Thing | Convention | Example |
|---|---|---|
| Route handlers | `ECHO_verb_noun` | `ECHO_get_video_data`, `ECHO_dashboard_stats` |
| Route registrars | `IncludeXxxRoutes` | `IncludeMediaRoutes`, `IncludeApiRoutes` |
| Exported functions | PascalCase | `FilterAndSortVideos`, `HashVideoFile` |
| Private helpers | camelCase | `handleServerError`, `getVideoMediaDir` |
| Structs / types | PascalCase | `ConfigStore`, `VideoData`, `JobBroker` |
| Package names | lowercase, matches dir | `config`, `db`, `routes`, `scanner` |
| Log prefixes | `[SCAN]`, `[MEDIA]`, `[TFIDF]`, `[EXEC]` | used in SSE emit lines |
| JSON tags | snake_case | `json:"date_added"`, `json:"is_linked"` |
| Local video map | `mp map[string]VideoData`, loop var `hsh` | consistent across handlers |
| Config snapshot | `cfg := store.Current()` | called inside closure, not outside |

---

## Gotchas

- **Cache returns only linked videos**: `GetCachedVideos` calls `ReadLinkedVideosMap` which filters via SQL `WHERE is_linked=1`. If you need unlinked records too (e.g. for field-preservation during a re-scan), use `ReadSerializedMapFromTable` directly.
- **Cache TTLs are hardcoded**: 15 s base, 3 s access — not configurable. Both must expire simultaneously for a cache miss.
- **Sort by VideoData fields**: common fields use `handleSortByDirectFields` (direct struct access, no allocation). Unknown fields fall back to `handleSortByVideoData` which does a JSON round-trip (`structsToMaps` → sort → `mapsToStructs`) — field name must match the JSON tag exactly.
- **Interaction sort drops videos without interactions**: `handleSortByInteractions` filters out any video that has no entry in the interactions map.
- **`normalizeVideoDataSlices` before writing**: Ensures slice fields marshal as `[]` not `null` for Python TF-IDF compatibility. Call it before `WriteSerializedRowToTable` on a `VideoData`.
- **No busy_timeout on SQLite**: The `PRAGMA busy_timeout` call is commented out in `db.go:49`. Under high concurrency, writes can fail with `SQLITE_BUSY` rather than waiting.
- **`PreviewMediaDir` is set once at startup**: It's passed directly to route groups as a string, not fetched from the store per-request. Changing it via the config editor sets `requiresRestart=true` and the old path stays active until restart.
- **`pyworker.Root()` is `log.Fatal`**: If `py/.venv` is missing, the server crashes at the first Python call (not at startup). Run `cd py && uv sync` before starting.
- **MKV remux is synchronous**: The on-the-fly ffmpeg pipe for `.mkv` holds the response open for the full stream duration. No timeout is set.
