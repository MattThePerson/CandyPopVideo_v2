package scanner

import (
    "io/fs"
    "path/filepath"
    "sort"
    "strings"
    "time"
)

// VideoFile represents a video file found during a filesystem walk.
type VideoFile struct {
    Path           string
    CollectionName string
    CollectionRoot string // absolute root dir for this collection entry
}

// collectVideoFiles walks all configured collection directories and returns
// every video file that passes the extension and path filters.
//
// If since is non-zero, only files whose direct parent directory has an mtime
// after since are collected (quick-scan mode). Subdirectories are always
// descended into regardless, so a touched dir nested inside an untouched
// parent is still found.
//
// If novelOnly is true (implies since is set), files are additionally filtered
// to those whose own mtime is after since.
//
// Returns the matched files and the count of distinct touched directories.
func collectVideoFiles(
    collections map[string][]string,
    extensions map[string]bool,
    pathFilter string,
    since time.Time,
    novelOnly bool,
) ([]VideoFile, int) {
    seen := map[string]bool{}
    dirMtime := map[string]time.Time{}
    touchedDirs := map[string]bool{}
    var results []VideoFile

    filterLower := strings.ToLower(strings.TrimSpace(pathFilter))

    for collName, roots := range collections {
        var includeDirs []string
        var excludeDirs []string

        for _, r := range roots {
            if strings.HasPrefix(r, "!") {
                excludeDirs = append(excludeDirs, filepath.Clean(r[1:]))
            } else {
                includeDirs = append(includeDirs, filepath.Clean(r))
            }
        }

        for _, root := range includeDirs {
            _ = filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
                if err != nil {
                    return nil
                }

                name := d.Name()

                if d.IsDir() {
                    if strings.HasPrefix(name, ".") {
                        return filepath.SkipDir
                    }
                    clean := filepath.Clean(path)
                    for _, ex := range excludeDirs {
                        if clean == ex || strings.HasPrefix(clean, ex+string(filepath.Separator)) {
                            return filepath.SkipDir
                        }
                    }
                    if info, err := d.Info(); err == nil {
                        dirMtime[path] = info.ModTime()
                    }
                    return nil
                }

                ext := strings.ToLower(filepath.Ext(name))
                if !extensions[ext] {
                    return nil
                }

                if filterLower != "" && !strings.Contains(strings.ToLower(path), filterLower) {
                    return nil
                }

                // Quick-scan directory mtime filter
                parent := filepath.Dir(path)
                if !since.IsZero() {
                    mt, ok := dirMtime[parent]
                    if !ok || !mt.After(since) {
                        return nil
                    }
                    touchedDirs[parent] = true
                }

                // Novel-files-only: also filter by file mtime
                if novelOnly && !since.IsZero() {
                    info, err := d.Info()
                    if err != nil || !info.ModTime().After(since) {
                        return nil
                    }
                }

                if seen[path] {
                    return nil
                }
                seen[path] = true

                results = append(results, VideoFile{
                    Path:           path,
                    CollectionName: collName,
                    CollectionRoot: root,
                })
                return nil
            })
        }
    }

    sort.Slice(results, func(i, j int) bool { return results[i].Path < results[j].Path })
    return results, len(touchedDirs)
}

// extensionSet converts a slice of extensions (e.g. ".mp4") to a lowercase lookup map.
func extensionSet(exts []string) map[string]bool {
    m := map[string]bool{}
    for _, e := range exts {
        m[strings.ToLower(e)] = true
    }
    return m
}
