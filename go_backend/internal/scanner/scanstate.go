package scanner

import (
    "encoding/json"
    "os"
    "path/filepath"
    "strings"
    "time"
)

type scanState struct {
    LastScanned string `json:"last_scanned"`
}

// ReadLastScanned reads the last_scanned timestamp from AppDataDir/info.json.
// Returns zero time on any error so the caller treats it as an unfiltered walk.
func ReadLastScanned(appDataDir string) time.Time {
    data, err := os.ReadFile(filepath.Join(appDataDir, "info.json"))
    if err != nil {
        return time.Time{}
    }
    var s scanState
    if err := json.Unmarshal(data, &s); err != nil {
        return time.Time{}
    }
    t, err := time.Parse(time.RFC3339, s.LastScanned)
    if err != nil {
        t, err = time.Parse("2006-01-02T15:04:05", s.LastScanned)
        if err != nil {
            return time.Time{}
        }
    }
    return t
}

// WriteLastScanned updates last_scanned in AppDataDir/info.json to t.
// Preserves any other keys already in the file.
func WriteLastScanned(appDataDir string, t time.Time) error {
    path := filepath.Join(appDataDir, "info.json")

    existing := map[string]any{}
    if data, err := os.ReadFile(path); err == nil {
        _ = json.Unmarshal(data, &existing)
    }
    existing["last_scanned"] = t.Format(time.RFC3339)

    data, err := json.MarshalIndent(existing, "", "  ")
    if err != nil {
        return err
    }
    return os.WriteFile(path, data, 0644)
}

// WriteNovelPathsLog overwrites AppDataDir/scan_novel_paths.txt with one path per line.
func WriteNovelPathsLog(appDataDir string, paths []string) error {
    logPath := filepath.Join(appDataDir, "scan_novel_paths.txt")
    content := strings.Join(paths, "\n")
    if len(paths) > 0 {
        content += "\n"
    }
    return os.WriteFile(logPath, []byte(content), 0644)
}
