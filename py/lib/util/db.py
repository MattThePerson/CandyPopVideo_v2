import sqlite3
import json


def read_videos_from_db(db_path: str) -> list[dict]:
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT data FROM videos")
        return [json.loads(row[0]) for row in cur]
