import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "songs.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS songs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    year INTEGER,
                    genre TEXT,
                    rating INTEGER DEFAULT 0,
                    cover_url TEXT,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            if conn.execute("SELECT COUNT(*) FROM songs").fetchone()[0] == 0:
                conn.executemany(
                    "INSERT INTO songs (title, artist, year, genre, rating, description) VALUES (?,?,?,?,?,?)",
                    [
                        ("Be Nice 2 Me", "Bladee", 2020, "Cloud rap", 5,
                         "Мечтательный трек в фирменной эстетике Drain Gang: вокал в автотюне и холодные синтезаторы."),
                        ("Peroxide", "Ecco2k", 2020, "Alt-pop", 5,
                         "Лёгкий и меланхоличный поп-трек с воздушным вокалом Ecco2k."),
                        ("Legendary Member", "Thaiboy Digital", None, "Cloud rap", 4,
                         "Трек Thaiboy Digital — одного из основателей Drain Gang."),
                    ],
                )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS popular_tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    artist TEXT NOT NULL,
                    title TEXT NOT NULL,
                    streams INTEGER NOT NULL,
                    cover_url TEXT,
                    as_of TEXT
                )
                """
            )
            if conn.execute("SELECT COUNT(*) FROM popular_tracks").fetchone()[0] == 0:
                conn.executemany(
                    "INSERT INTO popular_tracks (artist, title, streams, cover_url, as_of) VALUES (?,?,?,?,?)",
                    [
                        ("Bladee", "Be Nice 2 Me", 70_700_000, "/static/img/covers/be-nice-2-me.jpg", "13.11.2026"),
                        ("Thaiboy Digital", "Western Union", 43_800_000, "/static/img/covers/western-union.jpg", "13.11.2026"),
                        ("Ecco2k", "Peroxide", 38_300_000, "/static/img/covers/peroxide.jpg", "13.11.2026"),
                    ],
                )
            # Обложки для seed-песен (не затираем уже заданные вручную)
            for title, artist, cover in [
                ("Be Nice 2 Me", "Bladee", "/static/img/covers/be-nice-2-me.jpg"),
                ("Peroxide", "Ecco2k", "/static/img/covers/peroxide.jpg"),
                ("Legendary Member", "Thaiboy Digital", "/static/img/covers/legendary-member.jpg"),
            ]:
                conn.execute(
                    "UPDATE songs SET cover_url=? WHERE title=? AND artist=? AND (cover_url IS NULL OR cover_url='')",
                    (cover, title, artist),
                )
    finally:
        conn.close()
