"""Koneksi SQLite dengan pengaturan standar VORSA."""

import sqlite3
from pathlib import Path


def connect(path: str | Path) -> sqlite3.Connection:
    if str(path) != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")  # baca & tulis bisa bareng (bot + scheduler)
    return conn
