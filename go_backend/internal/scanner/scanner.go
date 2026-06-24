package scanner

import (
    "fmt"
    "os"
    "path/filepath"
    "time"

    string_parser "github.com/MattThePerson/string_parser"

    "cpv_backend/internal/config"
    "cpv_backend/internal/db"
    "cpv_backend/internal/pyworker"
    "cpv_backend/internal/schemas"
)

// ScanOptions mirrors the JSON body sent from the dashboard scan form.
type ScanOptions struct {
    RederiveMetadata bool   `json:"rederive_metadata"` // reparse filenames + reload sidecar JSON
    RedoAttributes   bool   `json:"redo_attributes"`
    Rehash           bool   `json:"rehash"`
    PathFilter       string `json:"path_filter"`
    QuickScan        bool   `json:"quick_scan"`       // filter walk by directory mtime > last scan
    NovelFilesOnly   bool   `json:"novel_files_only"` // additionally filter by file mtime > last scan
    ReadJSON         bool   `json:"read_json"`
}

// ScanLibraries walks all configured collections, processes each video file
// through the pipeline, and merges results into the database.
func ScanLibraries(cfg config.Config, opts ScanOptions, emit func(string)) error {
    isQuick := opts.QuickScan || opts.NovelFilesOnly

    var since time.Time
    if isQuick {
        since = ReadLastScanned(cfg.AppDataDir)
        emit(fmt.Sprintf("[SCAN] Quick scan — last scan: %s", since.Format("2006-01-02 15:04:05")))
    }

    emit("[SCAN] Walking collection folders…")
    files, touchedDirCount := collectVideoFiles(
        cfg.Collections,
        extensionSet(cfg.VideoExtensions),
        opts.PathFilter,
        since,
        opts.NovelFilesOnly,
    )

    if isQuick {
        emit(fmt.Sprintf("[SCAN] Found %d video files across %d touched folders", len(files), touchedDirCount))
    } else {
        emit(fmt.Sprintf("[SCAN] Found %d video files", len(files)))
    }

    emit("[SCAN] Loading existing database records…")
    existing, err := db.ReadSerializedMapFromTable[schemas.VideoData](cfg.DBPath, "videos")
    if err != nil {
        return fmt.Errorf("reading DB: %w", err)
    }
    pathToHash := buildPathToHash(existing)
    emit(fmt.Sprintf("[SCAN] Loaded %d existing records", len(existing)))

    loaded, novelPaths, errCount := processFiles(files, existing, pathToHash, cfg, opts, emit)

    if err := WriteNovelPathsLog(cfg.AppDataDir, novelPaths); err != nil {
        emit(fmt.Sprintf("[WARN] Could not write novel paths log: %v", err))
    }

    if !isQuick {
        emit("[SCAN] Sorting tags by collection frequency…")
        SortTagsByFrequency(loaded)
    }

    emit("[SCAN] Saving to database…")
    isFiltered := opts.PathFilter != "" || isQuick
    if err := MergeAndSave(cfg.DBPath, loaded, isFiltered); err != nil {
        return fmt.Errorf("saving to DB: %w", err)
    }

    if err := WriteLastScanned(cfg.AppDataDir, time.Now()); err != nil {
        emit(fmt.Sprintf("[WARN] Could not update last scan time: %v", err))
    }

    emit(fmt.Sprintf("[SCAN] Done. %d videos processed, %d novel, %d errors.", len(loaded), len(novelPaths), errCount))

    if isQuick {
        emit("[SCAN] Quick scan — skipping TF-IDF rebuild")
    } else if len(loaded) > 0 {
        rebuildTFIDF(cfg, emit)
    } else {
        emit("[TFIDF] No new files — skipping TF-IDF rebuild")
    }
    return nil
}

func buildPathToHash(existing map[string]schemas.VideoData) map[string]string {
    m := make(map[string]string, len(existing))
    for hash, vd := range existing {
        m[vd.Path] = hash
    }
    return m
}

func processFiles(
    files []VideoFile,
    existing map[string]schemas.VideoData,
    pathToHash map[string]string,
    cfg config.Config,
    opts ScanOptions,
    emit func(string),
) (map[string]*schemas.VideoData, []string, int) {
    loaded := map[string]*schemas.VideoData{}
    var novelPaths []string
    errCount := 0
    parser := string_parser.NewStringParserFromList(cfg.SceneFilenameFormats)

    for i, vf := range files {
        hash, vd, isNew, err := resolveVideo(vf, existing, pathToHash, opts)
        if err != nil {
            emit(fmt.Sprintf("[WARN] %s: %v", filepath.Base(vf.Path), err))
            errCount++
            continue
        }
        if isNew || opts.RedoAttributes {
            if attrs, err := ProbeAttributes(vf.Path); err != nil {
                emit(fmt.Sprintf("[WARN] ffprobe failed for %s: %v", filepath.Base(vf.Path), err))
            } else {
                applyAttributes(vd, attrs)
            }
        }
        if isNew || opts.RederiveMetadata {
            GetFileMetadata(vf.Path, vd, parser, opts.ReadJSON)
            vd.TagsFromPath = ExtractPathTags(vd)
        }
        if isNew {
            novelPaths = append(novelPaths, vf.Path)
        }
        loaded[hash] = vd
        if (i+1)%100 == 0 || i+1 == len(files) {
            emit(fmt.Sprintf("[SCAN] Processed %d / %d files", i+1, len(files)))
        }
    }
    return loaded, novelPaths, errCount
}

func applyAttributes(vd *schemas.VideoData, attrs VideoAttributes) {
    vd.DurationSeconds = attrs.DurationSeconds
    vd.Duration = attrs.Duration
    vd.FPS = attrs.FPS
    vd.Resolution = attrs.Resolution
    vd.Bitrate = attrs.Bitrate
    vd.FilesizeMB = attrs.FilesizeMB
}

func resolveVideo(
    vf VideoFile,
    existing map[string]schemas.VideoData,
    pathToHash map[string]string,
    opts ScanOptions,
) (hash string, vd *schemas.VideoData, isNew bool, err error) {
    if !opts.Rehash {
        if h, ok := pathToHash[vf.Path]; ok {
            if ex, ok2 := existing[h]; ok2 {
                return h, updatePathFields(&ex, vf), false, nil
            }
        }
    }
    hash, err = HashVideoFile(vf.Path)
    if err != nil {
        return "", nil, false, fmt.Errorf("hashing: %w", err)
    }
    if ex, ok := existing[hash]; ok && !opts.Rehash {
        return hash, updatePathFields(&ex, vf), false, nil
    }
    vd = &schemas.VideoData{
        Hash:           hash,
        Path:           vf.Path,
        Filename:       filepath.Base(vf.Path),
        DateAdded:      time.Now().Format("2006-01-02 15:04:05.000"),
        DateDownloaded: fileModTime(vf.Path),
        Collection:     vf.CollectionName,
        ParentDir:      vf.CollectionRoot,
        PathRelative:   relPathRelative(vf.Path, vf.CollectionRoot),
    }
    return hash, vd, true, nil
}

func updatePathFields(ex *schemas.VideoData, vf VideoFile) *schemas.VideoData {
    ex.Path = vf.Path
    ex.Filename = filepath.Base(vf.Path)
    ex.Collection = vf.CollectionName
    ex.ParentDir = vf.CollectionRoot
    ex.PathRelative = relPathRelative(vf.Path, vf.CollectionRoot)
    return ex
}

func relPathRelative(path, root string) string {
    rel, err := filepath.Rel(root, path)
    if err != nil {
        return filepath.Base(path)
    }
    return rel
}

func fileModTime(path string) string {
    info, err := os.Stat(path)
    if err != nil {
        return time.Now().Format("2006-01-02 15:04:05")
    }
    return info.ModTime().Format("2006-01-02 15:04:05")
}

func rebuildTFIDF(cfg config.Config, emit func(string)) {
    emit("[TFIDF] Building TF-IDF model…")
    _, err := pyworker.Exec(
        "-m", "cmd.generateTFIDF",
        "--db-path", cfg.DBPath,
        "--model-dir", cfg.AppDataDir,
        "--build-profiles",
    )
    if err != nil {
        emit(fmt.Sprintf("[TFIDF] Failed: %v", err))
        return
    }
    emit("[TFIDF] Model built successfully.")
}
