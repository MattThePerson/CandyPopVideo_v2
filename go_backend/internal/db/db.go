package db

import (
	"encoding/json"
	"fmt"

	"database/sql"

	_ "modernc.org/sqlite"
)

// (For a database that stores serialized json) Read row from table and unmarshal to struct
func ReadSerializedRowFromTable[S any](db_path string, table string, id string) (S, error) {

	var data S
	
	// Open db connection
	db, err := sql.Open("sqlite", db_path)
	if err != nil {
		return data, err
	}
	defer db.Close()

	// Make query
	var data_serialized string
	err = db.QueryRow("SELECT data FROM "+table+" WHERE id = ?", id).Scan(&data_serialized)
	if err != nil {
		return data, nil
		// return data, err
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
	db, err := sql.Open("sqlite", db_path)
	if err != nil {
		return items, err
	}
	defer db.Close()

	// Make query
	rows, err := db.Query("SELECT id, data FROM " + table)
	if err != nil {
		return items, err
	}
	defer rows.Close()

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
