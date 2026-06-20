# frontend/CLAUDE.md

Svelte 5 + TypeScript + Tailwind v4 frontend. These rules apply to all files under `frontend/`.

## Formatting

### Svelte file structure

Every Svelte file with both a `<script>` block and an HTML template must include a visual separator between them, and another before `<style>` if a style block exists:

```html
<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->
```

```html
<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->
```

Files with no `<script>` block omit the HTML separator. Files with no `<style>` block omit the CSS separator. Stub pages with neither skip both.

### Page.svelte path comment

Every `Page.svelte` file must have a comment on the very first line with its path relative to `src/`:

```html
<!-- pages/video/Page.svelte -->
```

### Props comment

If a component uses `$props()`, put `/* Props */` on the line immediately above it.

### Function comments

Add a short comment above any function whose purpose isn't immediately obvious from its name. Skip trivial one-liners and self-evident CRUD calls (e.g. `addLike()`). Do include a comment when:
- the function has a non-obvious implementation detail
- it works around a third-party quirk
- it uses optimistic UI (note "Optimistic — reverts on error")

---

## Directory structure

```
src/
    App.svelte              # Root: Header + routed <main> + Footer
    app.css                 # Tailwind v4 @theme tokens + @font-face + body base styles
    lib/
        router/
            routes.ts               # RouteDef[] — pattern → component map
            router.svelte.ts        # routerState, navigate(), initRouter(), matchRoute()
        types/
            video.ts                # VideoData, VideoInteractions interfaces
        stores/
            settings.svelte.ts      # cardVariant / cardSize / teaserMode / resultsPerPage (localStorage)
            configBuffer.svelte.ts  # unsaved config YAML content (localStorage, survives navigation)
        util/
            pager.svelte.ts         # createPager<T>() — reactive batch-loading helper
        components/
            Header.svelte           # Nav: logo, page links, random button, search, dashboard, settings gear
            SearchPanel.svelte      # Full search/filter bar used on /search
            VideoCard.svelte        # Variant dispatcher — currently always renders DefaultCard
            SimilarVideos.svelte    # TF-IDF similar-videos section with filter toggles + pager
            RenameOverlay.svelte    # Modal for F2 filename rename with undo toast
            ConfirmDialog.svelte    # Generic confirm modal (message, confirmLabel, onConfirm, onCancel)
            Spinner.svelte          # size?: number, bg?: string
            Footer.svelte
            cards/
                DefaultCard.svelte  # Full card: poster, sprite hover teaser, fav toggle, actors, tags
        player/
            PassionPlayer.js        # Bundled custom video player (not from npm)
            PassionPlayer.d.ts      # TS declarations
    pages/
        home/
            Page.svelte
        search/
            Page.svelte             # SearchPanel + card grid + PageNav; AbortController per search
            PageNav.svelte          # Prev / next page buttons
            types.ts                # SearchQuery, SearchResponse
        catalogue/
            Page.svelte             # Actors/studios/collections/tags browser with alpha letter groups
            CatalogueItem.svelte
            types.ts                # CatalogueTab, SortMode, CatalogueQuery, ItemInfo, Catalogue
        curated/
            Page.svelte             # Named saved searches loaded from config.yaml
            types.ts                # CuratedQuery, CuratedCollectionMeta
        video/
            Page.svelte             # Composes VideoPlayer + VideoDetails + RelatedVideos + SimilarVideos
            VideoPlayer.svelte      # PassionPlayer wrapper; loads seek thumbs + checks subtitles
            VideoDetails.svelte     # Title, studio/actor/tag chips, fav/like buttons, rating, description
            RelatedVideos.svelte    # Lazy-loaded carousel of structurally related videos
        dashboard/
            Page.svelte             # Stats overview + control cards + sticky SSE job log
            ScanSection.svelte      # Scan options card (reparse, rehash, path filter, …)
            MediaSection.svelte     # Media-gen card with type selector and coverage status table
            JobLog.svelte           # Scrolling SSE log panel
        config/
            Page.svelte             # CodeMirror 6 YAML editor (vim + oneDark) with save/validate/restore
```

---

## Router

Hand-rolled; no SvelteKit. `routerState` is a `$state({ path, search })` read directly by components. `navigate(fullPath, { replace? })` updates history and `routerState`. `initRouter()` wires `popstate` + delegated `<a>` click handling (intercepts same-origin anchors) — called once in `App.svelte`'s `onMount`, returns a cleanup fn. Routes match in declaration order (first wins); `:param` segments populate a `params` record passed as props to the page component. The `$lib` alias maps to `src/lib/`.

---

## Stores

Both use a **closure + getter/setter** pattern backed by `localStorage` (not Svelte `writable`). Each getter reads `$state`, each setter writes `$state` and `localStorage` in one call.

- **`settings`** — `cardVariant` (only `'default'` exists), `cardSize` (`small/medium/large/xl`), `teaserMode` (`sprite/video` — video mode not yet wired up), `resultsPerPage` (4/8/16/24/36).
- **`configBuffer`** — holds unsaved YAML editor content across navigations so edits survive clicking away to another page. `isDirty` is `$derived(content !== '')`; call `.clear()` on successful save. `savedAt` is an ISO timestamp updated on every content change.

---

## Types (`lib/types/video.ts`)

**`VideoData`** — mirrors the Go schema. Key fields for the UI: `hash` (primary key, used in all media/API URLs), `title`/`scene_title`/`filename` (display title in priority order), `actors`/`primary_actors`/`secondary_actors`, `tags`/`tags_from_filename`/`tags_from_path`/`tags_from_json`, `studio`, `line`, `collection`, `date_released`, `duration` (formatted string), `duration_seconds`, `resolution`, `bitrate`, `is_linked` (false if file not found on disk).

**`VideoInteractions`** — `viewtime` (cumulative seconds), `is_favourite`, `rating` (letter grade `C`–`S+`), `rating_score` (0–7 numeric), `markers` (`[time, color, tag][]`), `comments` (`[text, datetime][]`).

Per-page type files (`pages/*/types.ts`) define API request/response shapes — `SearchQuery`, `SearchResponse`, `CatalogueQuery`, `Catalogue`, `CuratedQuery`, etc.

---

## Key components

**`DefaultCard.svelte`** — fetches `VideoInteractions` on mount (non-critical; card renders without them). Favourite toggle is optimistic: flips immediately, reverts on error. Tags are truncated to ~50 chars; actors to 4; expand buttons reveal the rest. Tag coloring: `character: ` prefix → blue tint, `source: ` prefix → green tint. Accepts optional `width`/`aspectRatio` overrides in addition to `CardSize`.

**`SearchPanel.svelte`** — hydrates all fields from URL params on mount and on `popstate`. Builds a query string and calls `navigate('/search?...')`. Global keyboard shortcuts: `/` focuses the search input, `Enter` (when not already in a text field) focuses the include-terms field. Sort select and per-page select both fire `apply()` on `onchange`.

**`SimilarVideos.svelte`** — filter toggles (hide related, same studio, same collection, same actors) are applied client-side over the full TF-IDF results array. Uses `createPager` (batch 8). All four filter states are watched in a single `$effect` that calls `pager.reset()`.

**`RenameOverlay.svelte`** — validates against illegal characters (`\/:*?"<>|`), empty input, and unchanged stem in real time via `$derived`. Escape closes via a `window` keydown listener registered in `$effect`. On success the parent unmounts this component, so the loading state just stays until unmount.

**`ConfirmDialog.svelte`** — generic modal. Props: `message`, `confirmLabel` (default `'Confirm'`), `onConfirm`, `onCancel`. Backdrop click and `Escape` both call `onCancel`.

**`RelatedVideos.svelte`** — fetches up to five category types concurrently (movie-series, movie, line, actors, actor×studio). Each category with only 1 result is hidden. Carousel lazy-loads via `IntersectionObserver`; the current video's card is gold-outlined and scrolled into center on first activation.

---

## Player (`lib/player/PassionPlayer.js`)

Bundled custom player — not on npm. Instantiate with `new PassionPlayer({ hostEl, src, poster, title, subtitles_srt_src, autoplay, quiet, resumeKey })`. Key methods: `setSeekThumbs(vttText, dataUrl)`, `setSeekThumbsLoading(bool)`, `destroy()`. `resumeKey` is the video hash; the player uses it to restore playback position from `localStorage`.

`VideoPlayer.svelte` wraps it: checks for subtitles via `?check=true`, fetches the seek-thumb VTT + JPEG blob (converts blob to data URL via `FileReader` — `setSeekThumbs` requires a data URL, not a path), then instantiates the player. Fires `POST /api/interact/last-viewed/add/:hash` on mount.

---

## Theming

`app.css` defines Tailwind v4 `@theme` custom tokens. Core palette:

- `--color-nav-dark: #060A0A` — body/nav background
- `--color-off-white: #ecede3` — primary text
- `--color-actor-rose: #FF2C91` — actor chips
- `--color-play-orange: #D79C29` — selected tabs, carousel outline, rating badge
- `--color-search-cyan: #3EA7A7` — dashboard button background
- `--color-apply-purple: #752868` — apply button, favourite checkbox accent

Fonts: `Jaro` (logo, apply button, Jaro-rendered rating chips) and `Inter` (body copy, nav links, filter labels). Both are local TTFs declared with `@font-face` in `app.css`.

---

## Pages

- **`/search`** — `$effect` fires on every `routerState.search` change; uses `AbortController` to cancel in-flight requests. Page number is a URL param (`?page=N`).
- **`/catalogue`** — tab (`?type=`) and sort (`?sortby=`) are `$derived` from URL; all data is fetched once on mount and filtered/sorted client-side. Alphabetic sort produces letter-group navigation. A count threshold (`≥N videos`) hides sparse entries.
- **`/curated`** — fetches named saved searches from `/api/query/get/curated-collections` (sourced from `config.yaml`), then fires a search per entry to populate preview cards.
- **`/video/:hash`** — resolves `hash === 'random'` via `/api/get/random-video-hash` (replace history). Loads `VideoData` + `VideoInteractions` in parallel. F2 opens `RenameOverlay`; player is unmounted before rename to release file locks, remounted after.
- **`/dashboard`** — jobs start with a `POST`; if accepted, an `EventSource` on `/api/dashboard/job-stream` streams log lines. A `done` custom SSE event closes the stream and refreshes stats. 409 means a job is already running.
- **`/config`** — CodeMirror 6 with `lang-yaml`, `theme-one-dark`, `codemirror-vim`. Unsaved content lives in `configBuffer`. Save response includes `errors`, `warnings`, `requires_restart`. "Restore Defaults" overwrites config with the embedded template.

---

## Non-obvious patterns

**Sprite teaser (DefaultCard)** — on hover fires `GET /media/ensure/teaser-thumbs-small/:hash` (generates if missing), then loads the VTT + spritesheet. Cursor X maps to a frame index; the frame renders via `background-position` on an overlay div. `teaserState` gates re-entry so it runs at most once per card lifetime.

**PassionPlayer seek thumbs** — `setSeekThumbs(vttText, dataUrl)` requires an inline data URL, not a file path. `VideoPlayer.svelte` fetches the JPEG blob and converts it via `FileReader` before passing it in.

**Video rename (F2)** — `video/Page.svelte` sets `playerActive = false` and `await tick()` before sending the rename request, which unmounts the player and releases any OS file lock. The player remounts after the response regardless of success or failure. An undo toast is shown post-rename; undo itself is optimistic and re-shows the toast if the revert call fails.

**RelatedVideos carousel** — categories are fetched concurrently on mount; any with only 1 result (the current video itself) are suppressed. `IntersectionObserver` lazy-loads cards: only ±2 from the current video position are rendered initially. The current video's card gets a gold outline.

**SSE job stream (dashboard)** — a job starts with a `POST`; if accepted (not 409), `EventSource('/api/dashboard/job-stream')` is opened and log lines arrive via `onmessage`. A `done` custom event signals completion, closes the stream, and triggers a stats refresh.

**`createPager`** — `getItems` is a getter called reactively, not a snapshot. Call `pager.reset()` in a `$effect` whenever the source list changes to avoid a stale visible slice.
