package db

import (
    "database/sql"
    "encoding/json"
    "fmt"

    "cpv_backend/internal/schemas"
)

// interactionsSchema is the canonical DDL for the interactions table.
// Referenced by InitDB and MigrateInteractionsTable.
const interactionsSchema = `CREATE TABLE IF NOT EXISTS interactions (
    id              TEXT    PRIMARY KEY,
    last_viewed     TEXT    DEFAULT '',
    viewtime        REAL    DEFAULT 0,
    is_favourite    INTEGER DEFAULT 0,
    favourited_date TEXT    DEFAULT '',
    likes           INTEGER DEFAULT 0,
    rating          TEXT    DEFAULT '',
    rating_score    INTEGER DEFAULT 0,
    markers         TEXT    DEFAULT '[]',
    dated_markers   TEXT    DEFAULT '[]',
    comments        TEXT    DEFAULT '[]'
)`

type interColDef struct{ name, typ, def string }

var interExpectedCols = []interColDef{
    {"last_viewed", "TEXT", "''"},
    {"viewtime", "REAL", "0"},
    {"is_favourite", "INTEGER", "0"},
    {"favourited_date", "TEXT", "''"},
    {"likes", "INTEGER", "0"},
    {"rating", "TEXT", "''"},
    {"rating_score", "INTEGER", "0"},
    {"markers", "TEXT", "'[]'"},
    {"dated_markers", "TEXT", "'[]'"},
    {"comments", "TEXT", "'[]'"},
}

// ReadInteractionsRow reads a single VideoInteractions row by video hash.
// Returns sql.ErrNoRows if no record exists (callers handle this as a zero struct).
func ReadInteractionsRow(db_path, hash string) (schemas.VideoInteractions, error) {
    var inter schemas.VideoInteractions
    db, err := openDbConnection(db_path)
    if err != nil {
        return inter, err
    }
    defer db.Close()

    var isFavInt int
    var markersJSON, datedMarkersJSON, commentsJSON string
    err = db.QueryRow(
        `SELECT last_viewed, viewtime, is_favourite, favourited_date, likes, rating, rating_score,
                markers, dated_markers, comments FROM interactions WHERE id = ?`, hash,
    ).Scan(
        &inter.LastViewed, &inter.Viewtime, &isFavInt, &inter.FavouritedDate,
        &inter.Likes, &inter.Rating, &inter.RatingScore,
        &markersJSON, &datedMarkersJSON, &commentsJSON,
    )
    if err != nil {
        return inter, err
    }
    inter.Hash = hash
    inter.IsFavourite = isFavInt != 0
    json.Unmarshal([]byte(markersJSON), &inter.Markers)
    json.Unmarshal([]byte(datedMarkersJSON), &inter.DatedMarkers)
    json.Unmarshal([]byte(commentsJSON), &inter.Comments)
    return inter, nil
}

// ReadInteractionsMap reads all rows from the interactions table, keyed by hash.
func ReadInteractionsMap(db_path string) (map[string]schemas.VideoInteractions, error) {
    items := map[string]schemas.VideoInteractions{}
    db, err := openDbConnection(db_path)
    if err != nil {
        return items, err
    }
    defer db.Close()

    rows, err := db.Query(
        `SELECT id, last_viewed, viewtime, is_favourite, favourited_date, likes, rating, rating_score,
                markers, dated_markers, comments FROM interactions`,
    )
    if err != nil {
        return items, err
    }
    defer rows.Close()

    for rows.Next() {
        var inter schemas.VideoInteractions
        var isFavInt int
        var markersJSON, datedMarkersJSON, commentsJSON string
        if err := rows.Scan(
            &inter.Hash, &inter.LastViewed, &inter.Viewtime, &isFavInt, &inter.FavouritedDate,
            &inter.Likes, &inter.Rating, &inter.RatingScore,
            &markersJSON, &datedMarkersJSON, &commentsJSON,
        ); err != nil {
            return items, err
        }
        inter.IsFavourite = isFavInt != 0
        json.Unmarshal([]byte(markersJSON), &inter.Markers)
        json.Unmarshal([]byte(datedMarkersJSON), &inter.DatedMarkers)
        json.Unmarshal([]byte(commentsJSON), &inter.Comments)
        items[inter.Hash] = inter
    }
    return items, nil
}

// WriteInteractionsRow upserts a VideoInteractions row using individual columns.
func WriteInteractionsRow(db_path, hash string, inter schemas.VideoInteractions) error {
    db, err := openDbConnection(db_path)
    if err != nil {
        return err
    }
    defer db.Close()
    isFavInt := 0
    if inter.IsFavourite {
        isFavInt = 1
    }
    _, err = db.Exec(
        `INSERT OR REPLACE INTO interactions
         (id, last_viewed, viewtime, is_favourite, favourited_date, likes, rating, rating_score,
          markers, dated_markers, comments)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        hash, inter.LastViewed, inter.Viewtime, isFavInt, inter.FavouritedDate,
        inter.Likes, inter.Rating, inter.RatingScore,
        marshalOrEmpty(inter.Markers), marshalOrEmpty(inter.DatedMarkers), marshalOrEmpty(inter.Comments),
    )
    return err
}

func marshalOrEmpty(v any) string {
    b, err := json.Marshal(v)
    if err != nil || string(b) == "null" {
        return "[]"
    }
    return string(b)
}

// MigrateInteractionsTable migrates the interactions table from the old JSON-blob schema
// to the current columnar schema. Safe to call on already-migrated or empty databases.
func MigrateInteractionsTable(db_path string) error {
    db, err := openDbConnection(db_path)
    if err != nil {
        return err
    }
    defer db.Close()

    cols, err := getTableColumns(db, "interactions")
    if err != nil {
        return err
    }

    if cols["data"] && !cols["viewtime"] {
        fmt.Println("[DB] Migrating interactions table from JSON-blob to columnar schema...")
        if err := migrateInteractionsFromBlob(db); err != nil {
            return fmt.Errorf("interactions blob migration failed: %w", err)
        }
        fmt.Println("[DB] interactions migration complete")
        return nil
    }

    // New format: add any missing columns for forward-compat
    for _, col := range interExpectedCols {
        if !cols[col.name] {
            stmt := fmt.Sprintf("ALTER TABLE interactions ADD COLUMN %s %s DEFAULT %s", col.name, col.typ, col.def)
            if _, err := db.Exec(stmt); err != nil {
                return fmt.Errorf("adding column %s: %w", col.name, err)
            }
        }
    }
    return nil
}

func getTableColumns(db *sql.DB, table string) (map[string]bool, error) {
    rows, err := db.Query("PRAGMA table_info(" + table + ")")
    if err != nil {
        return nil, err
    }
    defer rows.Close()
    cols := map[string]bool{}
    for rows.Next() {
        var cid, notNull, pk int
        var name, typeName string
        var dfltValue sql.NullString
        if err := rows.Scan(&cid, &name, &typeName, &notNull, &dfltValue, &pk); err != nil {
            return nil, err
        }
        cols[name] = true
    }
    return cols, nil
}

func migrateInteractionsFromBlob(db *sql.DB) error {
    rows, err := db.Query("SELECT id, data FROM interactions")
    if err != nil {
        return err
    }
    type blobRow struct {
        id    string
        inter schemas.VideoInteractions
    }
    var oldRows []blobRow
    for rows.Next() {
        var id, data string
        if err := rows.Scan(&id, &data); err != nil {
            rows.Close()
            return err
        }
        var inter schemas.VideoInteractions
        if err := json.Unmarshal([]byte(data), &inter); err != nil {
            rows.Close()
            return fmt.Errorf("unmarshal interactions %s: %w", id, err)
        }
        oldRows = append(oldRows, blobRow{id, inter})
    }
    rows.Close()

    tx, err := db.Begin()
    if err != nil {
        return err
    }
    defer tx.Rollback()

    if _, err := tx.Exec(`CREATE TABLE interactions_new (
        id TEXT PRIMARY KEY, last_viewed TEXT DEFAULT '', viewtime REAL DEFAULT 0,
        is_favourite INTEGER DEFAULT 0, favourited_date TEXT DEFAULT '', likes INTEGER DEFAULT 0,
        rating TEXT DEFAULT '', rating_score INTEGER DEFAULT 0,
        markers TEXT DEFAULT '[]', dated_markers TEXT DEFAULT '[]', comments TEXT DEFAULT '[]'
    )`); err != nil {
        return err
    }

    stmt, err := tx.Prepare(
        `INSERT INTO interactions_new
         (id, last_viewed, viewtime, is_favourite, favourited_date, likes, rating, rating_score,
          markers, dated_markers, comments)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    )
    if err != nil {
        return err
    }
    defer stmt.Close()

    for _, r := range oldRows {
        isFavInt := 0
        if r.inter.IsFavourite {
            isFavInt = 1
        }
        if _, err := stmt.Exec(
            r.id, r.inter.LastViewed, r.inter.Viewtime, isFavInt, r.inter.FavouritedDate,
            r.inter.Likes, r.inter.Rating, r.inter.RatingScore,
            marshalOrEmpty(r.inter.Markers), marshalOrEmpty(r.inter.DatedMarkers),
            marshalOrEmpty(r.inter.Comments),
        ); err != nil {
            return err
        }
    }

    if _, err := tx.Exec("DROP TABLE interactions"); err != nil {
        return err
    }
    if _, err := tx.Exec("ALTER TABLE interactions_new RENAME TO interactions"); err != nil {
        return err
    }
    return tx.Commit()
}
