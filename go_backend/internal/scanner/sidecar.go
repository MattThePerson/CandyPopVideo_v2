package scanner

import (
    "encoding/json"
    "os"
    "path/filepath"
    "strings"

    "gopkg.in/yaml.v3"

    "cpv_backend/internal/schemas"
)

// FindSidecarFiles returns the ordered list of sidecar file paths for a video,
// highest-priority first. Returns nil if sourceID is empty or no files exist.
// Discovery walks upward from the video's directory to the filesystem root.
//
// Priority order:
//   - Source-ID file (first match wins across the whole walk)
//   - .metadata.json files, closest directory first
//
// See docs/video_info_loading.md for the full spec.
func FindSidecarFiles(videoPath, sourceID string) []string {
    videoDir := filepath.Dir(videoPath)

    var sourceIDFile string
    var genericFiles []string

    dir := videoDir
    for {
        // Step A: source-ID file — first match across the entire walk wins
        if sourceID != "" && sourceIDFile == "" {
            for _, candidate := range []string{
                filepath.Join(dir, sourceID+".json"),
                filepath.Join(dir, sourceID+".yaml"),
                filepath.Join(dir, ".metadata", sourceID+".json"),
                filepath.Join(dir, ".metadata", sourceID+".yaml"),
            } {
                if fileExists(candidate) {
                    sourceIDFile = candidate
                    break
                }
            }
        }

        // Step B: generic .metadata.json files — collect all that exist
        for _, candidate := range []string{
            filepath.Join(dir, ".metadata.json"),
            filepath.Join(dir, ".metadata", ".metadata.json"),
        } {
            if fileExists(candidate) {
                genericFiles = append(genericFiles, candidate)
            }
        }

        parent := filepath.Dir(dir)
        if parent == dir { // reached filesystem root (works on Windows and Unix)
            break
        }
        dir = parent
    }

    var result []string
    if sourceIDFile != "" {
        result = append(result, sourceIDFile)
    }
    result = append(result, genericFiles...)
    return result
}

// MergeSidecarFiles reads all sidecar files (highest-priority first) and merges
// their contents into a single map.
// Scalars: first (highest-priority) file wins.
// Arrays: accumulated across all files; only when both sides are slices.
// Unreadable or malformed files are skipped silently.
func MergeSidecarFiles(paths []string) map[string]any {
    merged := map[string]any{}
    for _, p := range paths {
        data, err := readSidecarFile(p)
        if err != nil {
            continue
        }
        for k, v := range data {
            existing, exists := merged[k]
            if !exists {
                merged[k] = v
                continue
            }
            // Only accumulate when both sides are slices
            existingSlice, existingIsSlice := toAnySlice(existing)
            incomingSlice, incomingIsSlice := toAnySlice(v)
            if existingIsSlice && incomingIsSlice {
                merged[k] = append(existingSlice, incomingSlice...)
            }
            // Scalar already set, or type mismatch → skip (first wins)
        }
    }
    return merged
}

// ApplySidecarToVideoData writes the merged sidecar map onto vd.
// The caller must have already reset TagsFromJSON/Views/Likes/Metadata to zero
// so this function starts from a clean slate.
//
// "tags" key → appended to TagsFromJSON (never goes into Metadata).
// Known scalar fields → written only if not already set by filename parsing.
// Known array fields → always combined and deduplicated.
// System/derived fields → always skipped.
// Unknown keys → Metadata map.
func ApplySidecarToVideoData(vd *schemas.VideoData, merged map[string]any) {
    // Extract "tags" before the main loop so it never falls into Metadata
    if tags := toStringSlice(merged["tags"]); len(tags) > 0 {
        vd.TagsFromJSON = append(vd.TagsFromJSON, tags...)
    }
    delete(merged, "tags")

    if vd.Metadata == nil {
        vd.Metadata = map[string]any{}
    }

    for k, v := range merged {
        if isSystemField(k) {
            continue
        }
        switch k {
        // Scalar fields that filename parsing can also set — filename wins
        case "title":
            if s, ok := toString(v); ok && vd.Title == "" {
                vd.Title = s
            }
        case "scene_title":
            if s, ok := toString(v); ok && vd.SceneTitle == "" {
                vd.SceneTitle = s
            }
        case "studio":
            if s, ok := toString(v); ok && vd.Studio == "" {
                vd.Studio = s
            }
        case "line":
            if s, ok := toString(v); ok && vd.Line == "" {
                vd.Line = s
            }
        case "date_released":
            if s, ok := toString(v); ok && vd.DateReleased == "" {
                vd.DateReleased = s
            }
        case "source_id":
            if s, ok := toString(v); ok && vd.SourceID == "" {
                vd.SourceID = s
            }
        case "dvd_code":
            if s, ok := toString(v); ok && vd.DVDCode == "" {
                vd.DVDCode = s
            }
        case "movie_title":
            if s, ok := toString(v); ok && vd.MovieTitle == "" {
                vd.MovieTitle = s
            }
        case "movie_series":
            if s, ok := toString(v); ok && vd.MovieSeries == "" {
                vd.MovieSeries = s
            }
        case "scene_number":
            if vd.SceneNumber == 0 {
                if n, ok := toInt(v); ok {
                    vd.SceneNumber = n
                }
            }

        // Scalar fields that filename parsing never sets — sidecar always writes
        case "description":
            if s, ok := toString(v); ok {
                vd.Description = s
            }
        case "views":
            if n, ok := toInt(v); ok {
                vd.Views = n
            }
        case "likes":
            if n, ok := toInt(v); ok {
                vd.Likes = n
            }

        // Array fields — always combine and deduplicate
        case "actors":
            vd.Actors = dedupeStrings(vd.Actors, toStringSlice(v))
        case "primary_actors":
            vd.PrimaryActors = dedupeStrings(vd.PrimaryActors, toStringSlice(v))
        case "secondary_actors":
            vd.SecondaryActors = dedupeStrings(vd.SecondaryActors, toStringSlice(v))
        case "genres":
            vd.Genres = dedupeStrings(vd.Genres, toStringSlice(v))

        default:
            vd.Metadata[k] = v
        }
    }
}

// --- private helpers ---------------------------------------------------------

func fileExists(path string) bool {
    _, err := os.Stat(path)
    return err == nil
}

func readSidecarFile(path string) (map[string]any, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, err
    }
    var result map[string]any
    switch strings.ToLower(filepath.Ext(path)) {
    case ".yaml", ".yml":
        err = yaml.Unmarshal(data, &result)
    default:
        err = json.Unmarshal(data, &result)
    }
    return result, err
}

func toString(v any) (string, bool) {
    s, ok := v.(string)
    return s, ok
}

func toInt(v any) (int, bool) {
    switch n := v.(type) {
    case int:
        return n, true
    case int64:
        return int(n), true
    case float64:
        return int(n), true
    }
    return 0, false
}

func toAnySlice(v any) ([]any, bool) {
    switch s := v.(type) {
    case []any:
        return s, true
    case []string:
        out := make([]any, len(s))
        for i, str := range s {
            out[i] = str
        }
        return out, true
    }
    return nil, false
}

func toStringSlice(v any) []string {
    switch s := v.(type) {
    case []string:
        return s
    case []any:
        out := make([]string, 0, len(s))
        for _, elem := range s {
            if str, ok := elem.(string); ok {
                out = append(out, str)
            }
        }
        return out
    }
    return nil
}

func dedupeStrings(existing, incoming []string) []string {
    seen := make(map[string]bool, len(existing))
    result := make([]string, len(existing))
    copy(result, existing)
    for _, s := range existing {
        seen[s] = true
    }
    for _, s := range incoming {
        if !seen[s] {
            seen[s] = true
            result = append(result, s)
        }
    }
    return result
}

// isSystemField returns true for VideoData fields that must never be written
// from sidecar data (identity, file attributes, derived/scanner-owned fields).
func isSystemField(key string) bool {
    switch key {
    case "hash", "path", "filename", "date_added",
        "duration", "duration_seconds", "filesize_mb", "fps", "bitrate",
        "height", "width", "resolution", "aspect_ratio",
        "is_vfr", "video_codec", "audio_codec", "pix_fmt", "color_transfer",
        "collection", "parent_dir", "path_relative", "is_linked",
        "tags", "tags_from_filename", "tags_from_path", "tags_from_json":
        return true
    }
    return false
}
