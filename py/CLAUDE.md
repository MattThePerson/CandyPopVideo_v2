# py/ — Python Workers

Minimal, self-contained subprocess workers called by the Go backend. No server, no config file reads, no shared state — each script receives everything it needs via explicit CLI flags and writes results to stdout (JSON) or disk.

## Invocation pattern

Scripts must be run from `py/` as the working directory, using the `-m` module flag:

```
cd py/
<python-exe> -m cmd.<script_name> --flag value ...
```

The Go backend always invokes them this way (`cmd.Dir = py/`), which is what makes `from lib.X import Y` resolve correctly. Never invoke scripts directly as files (`python cmd/foo.py`) — relative imports will break.

## Environment

Managed by `uv`. Setup:

```
cd py && uv sync
```

The venv lives at `py/.venv`. The executable Go uses is `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Linux). Dependencies (`pyproject.toml`): `scikit-learn`, `scipy`, `numpy`, `nltk`, `requests`, `beautifulsoup4`, `handymatt-media`, `send2trash`.

## cmd/ — Entrypoints

Each script is a single job. Shared conventions:
- All inputs come from CLI flags (`argparse`); no config files, no env vars, no app state
- Success: JSON to stdout, exit 0
- Failure: error message to stderr, exit 1 (JSON with `"error"` key for scripts that always output JSON)
- `main()` is always a plain callable so it can be tested without argparse
- Slow imports (`handymatt_media`, `sklearn`) are deferred inside `main()` where timing or skip logic makes it worthwhile

### `cmd.generateTFIDF`

```
python -m cmd.generateTFIDF --db-path <app.db> --model-dir <dir>
```

Reads all `is_linked` videos from SQLite, builds a TF-IDF model, and pickles two files to `<model-dir>`:
- `tdidf.pkl` — full `TFIDFModel` (vectorizer + matrix + `id_index_map`)
- `tdidf_matrix.pkl` — slim `TFIDFModelMatrix` (matrix + `id_index_map` only)

The split exists because `getSimilarVideos` only needs the matrix for cosine lookup and doesn't need to load sklearn's `TfidfVectorizer`. Prints plain-text progress to stdout; no JSON output.

### `cmd.getSimilarVideos`

```
python -m cmd.getSimilarVideos --model-path <tdidf_matrix.pkl> --target <hash>
```

Loads the slim matrix pickle and computes cosine similarity for one target hash. Returns up to 512 results, sorted by descending similarity score. All imports (`sklearn`, `scipy`, etc.) are deferred inside `main()` so the `import_ms` field in the report is accurate.

Output JSON:
```json
{
    "HashesList": ["abc123", ...],
    "SimsList": [0.94, ...],
    "Report": "import: 312.4ms  load: 88.1ms  compute: 12.3ms"
}
```

### `cmd.getActorInfo`

```
python -m cmd.getActorInfo --name "Jane Doe" --actor-info-dir <dir>
```

Cache-first: checks `<actor-info-dir>/<name>/info.json`; if absent, scrapes Babepedia and writes the result to disk. Returns `{}` (not an error) if the actor isn't found on Babepedia. The `504 Gateway Timeout` from Babepedia is surfaced as a raised exception (exit 1).

Output JSON: the info dict, or `{}`.

### `cmd.generatePreviewThumbs`

```
python -m cmd.generatePreviewThumbs \
    --video-path <path> --hash <hash> --media-dir <dir> \
    [--amount 5] [--n-frames 300] [--redo]
```

Calls `handymatt_media.media_generator.extractPreviewThumbs` to ML-select representative frames from the video. Output goes to `<media-dir>/0x<hash>/previewthumbs/`. Skip logic: if `>=10` files already exist in that folder, returns `{"success": true, "skipped": true}` without running inference. Pass `--redo` to force regeneration.

`handymatt-media` is imported inside `main()` only — the import is slow and the skip check doesn't need it.

Output JSON:
```json
{"success": true, "paths": ["/abs/path/thumb_0.jpg", ...]}
{"success": true, "paths": [], "skipped": true}
{"success": false, "error": "..."}
```

## lib/ — Shared Library

Used only internally by `cmd/` scripts. Never imported or called by Go directly.

### `lib.schemas.video_data`

`VideoData` dataclass, mirroring `go_backend/internal/schemas/video_data.go`. Key fields used by the recommender: `hash`, `title`, `studio`, `line`, `description`, `collection`, `actors`, `tags`, `is_linked`.

Always load from DB rows with `strict=False` to tolerate schema drift:
```python
VideoData.from_dict(row, strict=False)  # ignores unknown keys
```

### `lib.util.db`

`read_videos_from_db(db_path: str) -> list[dict]`

Connects to SQLite and reads every row from the `videos` table, deserializing the `data` JSON blob. Read-only — never writes. Returns raw dicts (not `VideoData` objects); callers convert them.

### `lib.util.general`

`pickle_save(obj, path)` / `pickle_load(path) -> obj | None`

Thin wrappers around `pickle.dump`/`load`. `pickle_load` returns `None` rather than raising if the file doesn't exist — callers must check.

### `lib.recommender`

**`tfidf_model.py`** — `TFIDFModel` dataclass: `vectorizer` (sklearn `TfidfVectorizer`), `matrix` (`csr_matrix`), `id_index_map` (`dict[hash_str, row_index]`).

**`model_matrix.py`** — `TFIDFModelMatrix` dataclass: `matrix` + `id_index_map` only. The lighter pickle used by `getSimilarVideos`.

**`tfidf.py`** — Model building and full-model queries.
- `generate_tfidf_model(videos)` — builds `TFIDFModel`. Token extraction per video draws from `title`, `studio`, `line`, `description`, `collection`, `actors`, `tags`. Each string is split into unigrams + bigrams, Snowball-stemmed, with CamelCase words expanded (e.g. `"HardCore"` → `"Hard Core"`). Numeric-only tokens are dropped from unigrams.
- `extract_model_matrix(model)` — strips the vectorizer to produce `TFIDFModelMatrix`.
- `get_related_videos_from_query_TFIDF(query_string, model)` — free-text query against a full model. Unknown query tokens are fuzzy-matched against vocabulary (same first character, `SequenceMatcher` ratio > 0.8).
- `get_similar_items_cosine(target_vect, matrix, id_index_map)` — cosine similarity via sklearn, returns ranked `list[tuple[hash, score]]`.

**`tfidf_light.py`** — `get_similar_videos_for_hash_TFIDF(hash, matrix_model)` — same cosine lookup but uses a hand-rolled sparse implementation (`matrix.dot(target.T)` + manual norm) to avoid importing sklearn at query time.

**`similarity.py`** — Performer embedding generation (mean-pool video TF-IDF vectors weighted by log video count) and `get_similar_performers`. **Not wired up — stub only.** The `similar-actors` and `similar-studios` Go routes return 501.

**`stopwords_eng.py`** — `STOPWORDS_ENG` constant (set of English stopwords). Not currently used in model building (stopwords param defaults to `[]` in `_extract_tokens_from_video`), but available.

### `lib.actor.actor_api`

Babepedia scraper and cache manager.

Public surface:
- `get_actor_info(name, actor_info_dir) -> dict | None` — cache read only
- `fetch_actor_info(name, actor_info_dir) -> dict | None` — scrape, cache write, gallery download

Cache layout:
```
<actor-info-dir>/
    <name>/
        info.json          # scraped metadata + gallery paths
        media/babepedia/   # downloaded gallery images (relative paths stored in info.json)
```

Scraped fields stored in `info.json`: `name`, `date_of_birth` (formatted `YYYY-MM-DD`), `aka`, `bio`, `comments`, `galleries` (relative paths), `babepedia` (raw scraped dict including `url`, `Born`, personal info block fields, `last_scraped`).
