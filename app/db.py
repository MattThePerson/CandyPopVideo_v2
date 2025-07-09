import sqlite3
import json
import os

from config import DB_PATH


def write_object_to_db(entry_id: str, data: dict, table: str):
    """ Write a single dictionary (JSON object) into a specified SQLite table. """
    with sqlite3.connect(DB_PATH) as conn:
        _ensure_table_exists(conn, table)
        cur = conn.cursor()
        cur.execute(f"INSERT OR REPLACE INTO {table} (id, data) VALUES (?, ?)", (entry_id, json.dumps(data),))
        conn.commit()


def write_dict_of_objects_to_db(objects_dict: dict[str, dict], table: str):
    """ Write a dictionary of objects into a specified SQLite table. """
    with sqlite3.connect(DB_PATH) as conn:
        _ensure_table_exists(conn, table)
        values = [ (id_, json.dumps(data)) for id_, data in objects_dict.items() ]
        conn.executemany(
            f"INSERT OR REPLACE INTO {table} (id, data) VALUES (?, ?)",
            values
        )


def read_object_from_db(entry_id: str, table: str) -> dict|None:
    """ Read a single JSON entry from the database by ID. """
    with sqlite3.connect(DB_PATH) as conn:
        _ensure_table_exists(conn, table)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cur = conn.cursor()
        cur.execute(f"SELECT data FROM {table} WHERE id = ?", (entry_id,))
        result = cur.fetchone()
        return json.loads(result["data"]) if result else None


def read_table_as_dict(table: str) -> dict[str, dict]:
    """ Read all JSON entries from the specified table and return as a dict of objects """
    with sqlite3.connect(DB_PATH) as conn:
        _ensure_table_exists(conn, table)
        cur = conn.cursor()
        cur.execute(f"SELECT id, data FROM {table}")
        return { row[0]: json.loads(row[1]) for row in cur }


# HELPERS

def _ensure_table_exists(conn: sqlite3.Connection, table: str) -> None:
    """ Ensures the specified table exists in the database with the correct schema. """
    if not os.path.exists(DB_PATH):
        print('[DB] Creating db at: "{}"'.format(DB_PATH))
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            id TEXT PRIMARY KEY,
            data TEXT
        )
    """)
