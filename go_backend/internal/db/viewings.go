package db

import (
    "fmt"
)

type viewingColDef struct{ name, typ, def string }

var viewingExpectedCols = []viewingColDef{
    {"video_hash",   "TEXT", "NULL"},
    {"datetime",     "TEXT", "NULL"},
    {"time_start",   "REAL", "0"},
    {"duration_sec", "REAL", "0"},
}

// MigrateViewingsTable handles two cases:
//   - Old "views" table exists → migrate rows into new "viewings" schema and drop views.
//   - "viewings" table exists → add any missing columns (forward-compat).
//
// If neither table exists, InitDB will create viewings fresh.
func MigrateViewingsTable(db_path string) error {
    db, err := openDbConnection(db_path)
    if err != nil {
        return err
    }
    defer db.Close()

    viewsCols, err := getTableColumns(db, "views")
    if err != nil {
        return err
    }
    viewingsCols, err := getTableColumns(db, "viewings")
    if err != nil {
        return err
    }

    if len(viewsCols) > 0 && len(viewingsCols) == 0 {
        fmt.Println("[DB] Migrating views → viewings table...")
        tx, err := db.Begin()
        if err != nil {
            return err
        }
        defer tx.Rollback()

        if _, err := tx.Exec(`CREATE TABLE viewings (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            video_hash   TEXT,
            datetime     TEXT,
            time_start   REAL DEFAULT 0,
            duration_sec REAL
        )`); err != nil {
            return fmt.Errorf("create viewings: %w", err)
        }
        if _, err := tx.Exec(`INSERT INTO viewings (video_hash, datetime, duration_sec)
            SELECT video_hash, timestamp, duration_sec FROM views`); err != nil {
            return fmt.Errorf("copy views data: %w", err)
        }
        if _, err := tx.Exec(`DROP TABLE views`); err != nil {
            return fmt.Errorf("drop views: %w", err)
        }
        if err := tx.Commit(); err != nil {
            return err
        }
        fmt.Println("[DB] views → viewings migration complete")
        return nil
    }

    if len(viewingsCols) > 0 {
        for _, col := range viewingExpectedCols {
            if !viewingsCols[col.name] {
                stmt := fmt.Sprintf("ALTER TABLE viewings ADD COLUMN %s %s DEFAULT %s", col.name, col.typ, col.def)
                if _, err := db.Exec(stmt); err != nil {
                    return fmt.Errorf("adding column %s: %w", col.name, err)
                }
            }
        }
    }

    return nil
}
