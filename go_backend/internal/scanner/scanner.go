package scanner

import (
    "fmt"
    "os"
    "os/exec"
    "path/filepath"
    "runtime"
    "strings"
    "time"

    "cpv_backend/internal/config"
    "cpv_backend/internal/db"
    "cpv_backend/internal/schemas"
)

// ScanOptions mirrors the JSON body sent from the dashboard scan form.
type ScanOptions struct {
    ReparseFilenames bool   `json:"reparse_filenames"`
    RereadJSON       bool   `json:"reread_json"`
    RedoAttributes   bool   `json:"redo_attributes"`
    Rehash           bool   `json:"rehash"`
    PathFilter       string `json:"path_filter"`
}

// ScanLibraries walks all configured collections, processes each video file
// through the pipeline, and merges results into the database.
func ScanLibraries(cfg config.Config, opts ScanOptions, emit func(string)) error {
    emit("[SCAN] Walking collection folders…")

    exts := extensionSet(cfg.VideoExtensions)
    files := collectVideoFiles(cfg.Collections, exts, opts.PathFilter)
    emit(fmt.Sprintf("[SCAN] Found %d video files", len(files)))

    // Load all existing DB records and build a path→hash reverse lookup
    emit("[SCAN] Loading existing database records…")
    existing, err := db.ReadSerializedMapFromTable[schemas.VideoData](cfg.DBPath, "videos")
    if err != nil {
        return fmt.Errorf("reading DB: %w", err)
    }
    pathToHash := map[string]string{}
    for hash, vd := range existing {
        pathToHash[vd.Path] = hash
    }
    emit(fmt.Sprintf("[SCAN] Loaded %d existing records", len(existing)))

    loaded := map[string]*schemas.VideoData{}
    errCount := 0

    for i, vf := range files {
        hash, vd, isNew, err := resolveVideo(vf, existing, pathToHash, opts)
        if err != nil {
            emit(fmt.Sprintf("[WARN] %s: %v", filepath.Base(vf.Path), err))
            errCount++
            continue
        }

        // Video attributes
        if isNew || opts.RedoAttributes {
            attrs, err := ProbeAttributes(vf.Path)
            if err != nil {
                emit(fmt.Sprintf("[WARN] ffprobe failed for %s: %v", filepath.Base(vf.Path), err))
            } else {
                vd.DurationSeconds = attrs.DurationSeconds
                vd.Duration = attrs.Duration
                vd.FPS = attrs.FPS
                vd.Resolution = attrs.Resolution
                vd.Bitrate = attrs.Bitrate
                vd.FilesizeMB = attrs.FilesizeMB
            }
        }

        // Filename parsing
        if isNew || opts.ReparseFilenames {
            stem := strings.TrimSuffix(filepath.Base(vf.Path), filepath.Ext(vf.Path))
            tags, cleanStem := ExtractTags(stem)
            vd.TagsFromFilename = tags

            // Build rel_parent/cleanStem for the parser
            relParent := relativeParent(vf.Path, vf.CollectionRoot)
            var parseInput string
            if relParent != "" {
                parseInput = relParent + "/" + cleanStem
            } else {
                parseInput = cleanStem
            }
            parsed := ParseFilename(parseInput, cfg.SceneFilenameFormats)
            PopulateFromParseResult(vd, parsed)
        }

        // Path tags (always — cheap, and depends on Actors/Studio set above)
        vd.TagsFromPath = ExtractPathTags(vd)

        loaded[hash] = vd

        if (i+1)%100 == 0 || i+1 == len(files) {
            emit(fmt.Sprintf("[SCAN] Processed %d / %d files", i+1, len(files)))
        }
    }

    emit("[SCAN] Sorting tags by collection frequency…")
    SortTagsByFrequency(loaded)

    emit("[SCAN] Saving to database…")
    if err := MergeAndSave(cfg.DBPath, loaded, opts.PathFilter != ""); err != nil {
        return fmt.Errorf("saving to DB: %w", err)
    }

    emit(fmt.Sprintf("[SCAN] Done. %d videos processed, %d errors.", len(loaded), errCount))
    rebuildTFIDF(emit)
    return nil
}

// resolveVideo determines the hash and VideoData for a given file, either by
// reusing an existing DB record or creating a fresh one.
func resolveVideo(
    vf VideoFile,
    existing map[string]schemas.VideoData,
    pathToHash map[string]string,
    opts ScanOptions,
) (hash string, vd *schemas.VideoData, isNew bool, err error) {

    // Try to reuse hash from existing record by path
    if !opts.Rehash {
        if h, ok := pathToHash[vf.Path]; ok {
            if ex, ok2 := existing[h]; ok2 {
                // Update path-derivable fields in case the file moved within the collection
                ex.Path = vf.Path
                ex.Filename = filepath.Base(vf.Path)
                ex.Collection = vf.CollectionName
                ex.ParentDir = vf.CollectionRoot
                ex.PathRelative = relPathRelative(vf.Path, vf.CollectionRoot)
                return h, &ex, false, nil
            }
        }
    }

    // Compute hash
    hash, err = HashVideoFile(vf.Path)
    if err != nil {
        return "", nil, false, fmt.Errorf("hashing: %w", err)
    }

    // Check if this hash already exists in DB (file was renamed)
    if ex, ok := existing[hash]; ok && !opts.Rehash {
        ex.Path = vf.Path
        ex.Filename = filepath.Base(vf.Path)
        ex.Collection = vf.CollectionName
        ex.ParentDir = vf.CollectionRoot
        ex.PathRelative = relPathRelative(vf.Path, vf.CollectionRoot)
        return hash, &ex, false, nil
    }

    // Brand-new video
    dateAdded := fileCtime(vf.Path)
    rel := relPathRelative(vf.Path, vf.CollectionRoot)

    vd = &schemas.VideoData{
        Hash:           hash,
        Path:           vf.Path,
        Filename:       filepath.Base(vf.Path),
        DateAdded:      dateAdded,
        Collection:     vf.CollectionName,
        ParentDir: vf.CollectionRoot,
        PathRelative:   rel,
        IsLinked:       true,
    }
    return hash, vd, true, nil
}

// relativeParent returns the directory portion of path relative to root,
// using forward slashes, or "" if path is directly in root.
func relativeParent(path, root string) string {
    rel := relPathRelative(path, root)
    rel = filepath.ToSlash(rel)
    if idx := strings.LastIndex(rel, "/"); idx >= 0 {
        return rel[:idx]
    }
    return ""
}

// relPathRelative returns the path of a file relative to its collection root,
// with the OS path separator (used for PathRelative field).
func relPathRelative(path, root string) string {
    rel, err := filepath.Rel(root, path)
    if err != nil {
        return filepath.Base(path)
    }
    return rel
}

// fileCtime returns the file creation/change time as "YYYY-MM-DD HH:MM".
func fileCtime(path string) string {
    info, err := os.Stat(path)
    if err != nil {
        return time.Now().Format("2006-01-02 15:04")
    }
    return info.ModTime().Format("2006-01-02 15:04")
}

// rebuildTFIDF shells out to the Python worker to regenerate the TF-IDF model
// so similar-video lookups stay current after a scan.
func rebuildTFIDF(emit func(string)) {
    emit("[TFIDF] Building TF-IDF model…")
    out, err := exec.Command(localPythonInterpreter(), "-m", "python_src.worker", "--generate-tfidf").CombinedOutput()
    if err != nil {
        emit(fmt.Sprintf("[TFIDF] Failed: %v — %s", err, strings.TrimSpace(string(out))))
        return
    }
    emit("[TFIDF] Model built successfully.")
}

// localPythonInterpreter returns the path to the project .venv interpreter.
// Mirrors getLocalPythonInterpreter in routes/0_routes_helpers.go.
func localPythonInterpreter() string {
    if runtime.GOOS == "windows" {
        return `.venv\Scripts\python.exe`
    }
    return ".venv/bin/python3"
}
