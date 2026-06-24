package db

import (
    "fmt"
    "os"
    "path/filepath"
    "strings"
    "time"
)

const backupThreshold = 14 * 24 * time.Hour

// CheckAndBackup creates a timestamped copy of dbPath in backupDir using
// VACUUM INTO if the newest existing backup is older than 14 days (or none exist).
// Returns an error if backupDir doesn't exist; never creates it automatically.
func CheckAndBackup(dbPath, backupDir string) error {
    if backupDir == "" {
        return nil
    }

    if _, err := os.Stat(backupDir); os.IsNotExist(err) {
        return fmt.Errorf("backup dir does not exist: %s", backupDir)
    }

    newest, err := newestBackupTime(backupDir)
    if err != nil {
        return fmt.Errorf("scanning backup dir: %w", err)
    }
    if !newest.IsZero() && time.Since(newest) < backupThreshold {
        return nil
    }

    destName := fmt.Sprintf("app_%s.db", time.Now().Format("2006-01-02_150405"))
    destPath := filepath.Join(backupDir, destName)

    conn, err := openDbConnection(dbPath)
    if err != nil {
        return fmt.Errorf("opening db for backup: %w", err)
    }
    defer conn.Close()

    if _, err := conn.Exec(fmt.Sprintf("VACUUM INTO '%s'", destPath)); err != nil {
        return fmt.Errorf("VACUUM INTO failed: %w", err)
    }

    fmt.Printf("[BACKUP] Created %s\n", destPath)
    return nil
}

func newestBackupTime(dir string) (time.Time, error) {
    entries, err := os.ReadDir(dir)
    if err != nil {
        return time.Time{}, err
    }
    var newest time.Time
    for _, e := range entries {
        if e.IsDir() || !strings.HasPrefix(e.Name(), "app_") || !strings.HasSuffix(e.Name(), ".db") {
            continue
        }
        info, err := e.Info()
        if err != nil {
            continue
        }
        if info.ModTime().After(newest) {
            newest = info.ModTime()
        }
    }
    return newest, nil
}
