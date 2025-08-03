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


// WriteSerializedRowToTable will marshal (serialize) data from a complex type and write to 'serialized' db
func WriteSerializedRowToTable[S any](db_path string, table string, id string, data_struct S) error {

	// Open db connection
	db, err := sql.Open("sqlite", db_path)
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


// InsertDataIntoTable
func InsertDataIntoTable(db_path string, table string, data map[string]any) error {

	// Open db connection
	db, err := sql.Open("sqlite", db_path)
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

