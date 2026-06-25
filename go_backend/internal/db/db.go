package db

import (
	"encoding/json"
	"fmt"

	"database/sql"

	"cpv_backend/internal/schemas"
	_ "modernc.org/sqlite"
)


// InitDB creates all required tables if they don't already exist.
// Call once at server startup so the DB is ready regardless of whether
// the Python worker has ever run.
func InitDB(db_path string) error {
    db, err := openDbConnection(db_path)
    if err != nil {
        return err
    }
    defer db.Close()

    stmts := []string{
        `CREATE TABLE IF NOT EXISTS videos (id TEXT PRIMARY KEY, date_added TEXT, path TEXT NOT NULL DEFAULT '', is_linked INTEGER NOT NULL DEFAULT 1, data TEXT)`,
        interactionsSchema,
        `CREATE TABLE IF NOT EXISTS viewings (id INTEGER PRIMARY KEY AUTOINCREMENT, video_hash TEXT, datetime TEXT, time_start REAL, duration_sec REAL)`,
    }
    for _, stmt := range stmts {
        if _, err := db.Exec(stmt); err != nil {
            return err
        }
    }

    return nil
}


func openDbConnection(db_path string) (*sql.DB, error) {
	db, err := sql.Open("sqlite", db_path)
	if err != nil {
		return db, err
	}
	// Write Ahead Logging mode (enables concurrent reads ans writes)
	_, err = db.Exec("PRAGMA journal_mode = WAL;")
	if err != nil {
		return db, err
	}
	// busy timeout
	// _, err = db.Exec("PRAGMA busy_timeout = 5000;")
	// if err != nil {
	// 	return db, err
	// }
	return db, nil
}


// (For a database that stores serialized json) Read row from table and unmarshal to struct
func ReadSerializedRowFromTable[S any](db_path string, table string, id string) (S, error) {

	var data S
	
	// Open db connection
	db, err := openDbConnection(db_path)
	if err != nil {
		return data, err
	}
	defer db.Close()

	// Make query
	var data_serialized string
	err = db.QueryRow("SELECT data FROM "+table+" WHERE id = ?", id).Scan(&data_serialized)
	if err != nil {
		return data, err
	}
	
	// Unmarshal to schema
	err = json.Unmarshal([]byte(data_serialized), &data)
	if err != nil {
		return data, err
	}

	return data, nil
	
}

// (For a database that stores serialized json) Read all rows from a table, unmarshal rows to struct and return as map
func ReadSerializedMapFromTable[S any](db_path string, table string) (map[string]S, error) {

	items := map[string]S{}
	
	// Open db connection
	db, err := openDbConnection(db_path)
	if err != nil {
		return items, err
	}
	defer db.Close()

	// Make query
	rows, err := db.Query("SELECT id, data FROM " + table)
	if err != nil {
		return items, err
	}

	// Process rows
	for rows.Next() {
		var id string
		var data_serialized string
		if err := rows.Scan(&id, &data_serialized); err != nil {
			return items, err
		}

		// Unmarshal to schema
		var data S
		if err := json.Unmarshal([]byte(data_serialized), &data); err != nil {
			fmt.Println("hash: " + id)
			return items, err
		}
		items[id] = data
	}

	return items, nil
	
}


// WriteSerializedRowToTable will marshal (serialize) data from a complex type and write to 'serialized' db
func WriteSerializedRowToTable[S any](db_path string, table string, id string, data_struct S) error {

	// Open db connection
	db, err := openDbConnection(db_path)
	if err != nil {
		return err
	}
	defer db.Close()

	// marshal data
	data, err := json.Marshal(data_struct)
	if err != nil {
		return err
	}
	
	// write row
	_, err = db.Exec("INSERT OR REPLACE INTO "+table+" (id, data) VALUES (?, ?)", id, data)
	if err != nil {
		return err
	}
	
	return nil
}


// WriteVideoRow writes a VideoData record to the videos table, always marking
// it as is_linked=1. Shadow columns (path, date_added) are kept in sync with
// the JSON blob so SQL-level queries and DB-browser sorting work correctly.
func WriteVideoRow(db_path string, hash string, vd schemas.VideoData) error {
    db, err := openDbConnection(db_path)
    if err != nil {
        return err
    }
    defer db.Close()

    data, err := json.Marshal(vd)
    if err != nil {
        return err
    }

    _, err = db.Exec(
        "INSERT OR REPLACE INTO videos (id, path, is_linked, date_added, data) VALUES (?, ?, 1, ?, ?)",
        hash, vd.Path, vd.DateAdded, data,
    )
    return err
}


// BatchWriteVideoRows writes all provided VideoData records in a single
// transaction. Always marks each row as is_linked=1.
func BatchWriteVideoRows(dbPath string, videos map[string]schemas.VideoData) error {
    db, err := openDbConnection(dbPath)
    if err != nil {
        return err
    }
    defer db.Close()

    tx, err := db.Begin()
    if err != nil {
        return err
    }
    defer tx.Rollback()

    stmt, err := tx.Prepare("INSERT OR REPLACE INTO videos (id, path, is_linked, date_added, data) VALUES (?, ?, 1, ?, ?)")
    if err != nil {
        return err
    }
    defer stmt.Close()

    for hash, vd := range videos {
        data, err := json.Marshal(vd)
        if err != nil {
            return err
        }
        if _, err := stmt.Exec(hash, vd.Path, vd.DateAdded, data); err != nil {
            return err
        }
    }
    return tx.Commit()
}


// SetAllUnlinked marks every row in the videos table as is_linked=0 in a single
// SQL statement. Called at the start of a full (unfiltered) scan.
func SetAllUnlinked(db_path string) error {
    db, err := openDbConnection(db_path)
    if err != nil {
        return err
    }
    defer db.Close()
    _, err = db.Exec("UPDATE videos SET is_linked = 0")
    return err
}


// ReadLinkedVideosMap returns only linked videos (is_linked=1), deserializing
// each JSON blob. Used by the cache and mediagen batch.
func ReadLinkedVideosMap(db_path string) (map[string]schemas.VideoData, error) {
    items := map[string]schemas.VideoData{}

    db, err := openDbConnection(db_path)
    if err != nil {
        return items, err
    }
    defer db.Close()

    rows, err := db.Query("SELECT id, data FROM videos WHERE is_linked = 1")
    if err != nil {
        return items, err
    }

    for rows.Next() {
        var id string
        var data_serialized string
        if err := rows.Scan(&id, &data_serialized); err != nil {
            return items, err
        }
        var data schemas.VideoData
        if err := json.Unmarshal([]byte(data_serialized), &data); err != nil {
            fmt.Println("hash: " + id)
            return items, err
        }
        items[id] = data
    }
    return items, nil
}


// CountVideosByLinkedStatus returns the number of linked and unlinked videos
// via a single GROUP BY query. Used by dashboard stats.
func CountVideosByLinkedStatus(db_path string) (linked int, unlinked int, err error) {
    db, err := openDbConnection(db_path)
    if err != nil {
        return 0, 0, err
    }
    defer db.Close()

    rows, err := db.Query("SELECT is_linked, COUNT(*) FROM videos GROUP BY is_linked")
    if err != nil {
        return 0, 0, err
    }
    for rows.Next() {
        var status, count int
        if scanErr := rows.Scan(&status, &count); scanErr != nil {
            return 0, 0, scanErr
        }
        if status == 1 {
            linked = count
        } else {
            unlinked = count
        }
    }
    return linked, unlinked, nil
}


// InsertDataIntoTable
func InsertDataIntoTable(db_path string, table string, data map[string]any) error {

	// Open db connection
	db, err := openDbConnection(db_path)
	if err != nil {
		return err
	}
	defer db.Close()

	// get strings
	columns_str := ""
	qmarks_str := ""
	values := []any{}
	FIRST_FLAG := true
	for k, v := range data {
		values = append(values, v)
		if FIRST_FLAG {
			FIRST_FLAG = false
		} else {
			columns_str += ", "
			qmarks_str += ", "
		}
		columns_str += k
		qmarks_str += "?"
	}
	
	// write row
	command := fmt.Sprintf("INSERT INTO %s (%s) VALUES (%s)", table, columns_str, qmarks_str)
	_, err = db.Exec(command, values...)
	if err != nil {
		return err
	}
	
	return nil
}

