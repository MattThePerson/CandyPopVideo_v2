# Video Info Loading

Describes how the scanner derives and combines metadata for each video from all sources.

---

## Sources

A video's metadata is built from four sources, applied in this order:

| # | Source | Trigger | Fields populated |
|---|---|---|---|
| 1 | **ffprobe** | New video, or `RedoAttributes` | `Duration`, `FPS`, `Resolution`, `Bitrate`, `FilesizeMB` |
| 2 | **Filename parse** | New video, or `RederiveMetadata` | `Title`, `Studio`, `Actors`, `SourceID`, `DateReleased`, etc. |
| 3 | **Path tags** | Always (cheap, always re-derived) | `TagsFromPath` |
| 4 | **Sidecar JSON/YAML** | New video, or `RederiveMetadata` | `TagsFromJSON`, `Views`, `Likes`, `Description`, any matching field, remainder → `Metadata` |

Filename parsing and sidecar loading are always done together (controlled by the single `RederiveMetadata` flag). Doing one without the other risks leaving the record in an inconsistent state, since both write to overlapping fields.

---

## 1. Filename parsing

Each video's stem (filename minus extension and `#Tag` tokens) is matched against the ordered list of `scene_filename_formats` patterns (most-specific first, first match wins). The match result is mapped onto `VideoData` fields via `PopulateFromParseResult`.

Before reparsing, all filename-derived fields are explicitly cleared (`clearFilenameFields`) so stale values from a previous parse don't survive when the new parse omits them.

Fields that can be set by filename parsing: `Title`, `SceneTitle`, `SceneNumber`, `MovieTitle`, `MovieSeries`, `Studio`, `Line`, `DateReleased`, `SourceID`, `DVDCode`, `Actors`, `PrimaryActors`.

---

## 2. Path tags

Directory names between the collection root and the video file are extracted as `TagsFromPath`, excluding names already captured as `Actors`, `Studio`, or `Line`. This step always runs — it's cheap and its result depends on `Actors`/`Studio` set in the filename parse step above.

---

## 3. Sidecar JSON/YAML discovery

Sidecar loading only applies to videos that have a `SourceID` (extracted from filename parsing).

### Step A — Source-ID file (walk up, first match wins)

Starting from the video's directory, walk up toward the filesystem root. At each level check — in order:

1. `<dir>/<source_id>.json`
2. `<dir>/<source_id>.yaml`
3. `<dir>/.metadata/<source_id>.json`
4. `<dir>/.metadata/<source_id>.yaml`

Stop at the first file found. Only one source-ID file is ever loaded.

### Step B — Generic `.metadata.json` files (walk up, collect all)

Walk the same tree from the video's directory up to the filesystem root. At each level collect every file that exists:

1. `<dir>/.metadata.json`
2. `<dir>/.metadata/.metadata.json`

No early stop — all found files are collected.

### Step C — Merging sidecar files together

Assemble the full candidate list in priority order (highest first):

| Priority | File |
|---|---|
| 1 (highest) | Source-ID file (Step A), if found |
| 2 | `<video dir>/.metadata.json` |
| 3 | `<video dir>/.metadata/.metadata.json` |
| 4 | `<parent dir>/.metadata.json` |
| 5 | `<parent dir>/.metadata/.metadata.json` |
| … | … up to root (lowest) |

Priority rules:
- Closer to the video beats farther away
- Source-ID file beats any `.metadata.json` file at any depth
- `<dir>/x` beats `<dir>/.metadata/x` beats `<parent>/x` beats `<parent>/.metadata/x`

Iterate through the list and merge the raw JSON/YAML data into a single map:
- **Scalar** (string, int, bool, etc.): write only if the key is not already in the merged map — first (highest-priority) value wins.
- **Array**: accumulate across all files regardless of priority. Only combine if the existing accumulated value is also an array; if a later file supplies a non-array for an already-array key, skip it.

---

## 4. Applying sidecar data to VideoData

Once the sidecar files are merged into a single raw map, apply it to the `VideoData` record:

1. **Extract `"tags"`** — the `"tags"` key is handled specially. Its value (expected to be an array of strings) is extracted from the map and appended to `TagsFromJSON`. It is not placed into `Metadata`.

2. **Map known fields** — for every remaining key that matches a named `VideoData` JSON field (e.g. `"title"`, `"description"`, `"views"`, `"likes"`, `"studio"`, `"actors"`, etc.):
   - If the field is **scalar** and already has a non-zero value from filename parsing: **skip** (filename wins).
   - If the field is **scalar** and not yet set: write the sidecar value.
   - If the field is **array/combinable** (e.g. `Actors`): append sidecar values to existing, deduplicating.

3. **Remainder → `Metadata`** — any key not matched to a known `VideoData` field is stored in `Metadata map[string]any`. If a key exists in both the existing `Metadata` and the sidecar, the sidecar value is skipped (existing wins — consistent with scalar rule above).

> **Note:** The exact field-mapping behaviour was revised several times in the previous Python implementation and may need further tuning. The rule above (filename beats sidecar for scalars, combine for arrays, rest into Metadata) is intentionally simple and well-defined so deviations are easy to reason about. Revisit this section if edge cases arise.

---

## 5. Final Tags construction

After all sources are applied, `Tags` is rebuilt as the deduplicated union of the three tag-source slices, in this order (all sources first-wins for dedup):

```
Tags = dedup(TagsFromFilename + TagsFromPath + TagsFromJSON)
```

Each source list is independently sorted by descending collection-wide tag frequency before the union is computed.

> `Genres` is currently stored separately and is not folded into `Tags`. This may be revisited.

---

## Re-derive flag

The dashboard "re-derive metadata" option (`RederiveMetadata`) triggers both filename reparsing and sidecar re-reading for all already-known videos. New videos always have both applied on first scan regardless of this flag.

The old separate `ReparseFilenames` and `RereadJSON` flags are replaced by this single flag because the two operations write to overlapping fields and must be kept in sync.
