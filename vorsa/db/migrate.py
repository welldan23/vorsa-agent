"""Migrasi skema SQLite.

File `migrations/NNN_nama.sql` dijalankan berurutan sekali saja; nomor terakhir yang
sudah dijalankan dicatat di `PRAGMA user_version`.
"""

import logging
import re
import sqlite3
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
_NAME = re.compile(r"^(\d{3})_[\w-]+\.sql$")

log = logging.getLogger(__name__)


def list_migrations() -> list[tuple[int, Path]]:
    found = []
    for path in MIGRATIONS_DIR.iterdir():
        match = _NAME.match(path.name)
        if match:
            found.append((int(match.group(1)), path))
    found.sort()
    numbers = [n for n, _ in found]
    if numbers != list(range(1, len(numbers) + 1)):
        raise RuntimeError(f"Nomor migrasi harus urut mulai 001 tanpa loncat: {numbers}")
    return found


def current_version(conn: sqlite3.Connection) -> int:
    return conn.execute("PRAGMA user_version").fetchone()[0]


def apply_migrations(conn: sqlite3.Connection) -> int:
    """Jalankan migrasi yang belum diterapkan. Mengembalikan versi skema akhir."""
    version = current_version(conn)
    for number, path in list_migrations():
        if number <= version:
            continue
        log.info("Menerapkan migrasi %s", path.name)
        # executescript tidak ikut transaksi Python, jadi BEGIN/COMMIT ditulis eksplisit
        # supaya migrasi yang gagal di tengah tidak meninggalkan skema setengah jadi.
        try:
            conn.executescript(f"BEGIN;\n{path.read_text()}\nPRAGMA user_version = {number};\nCOMMIT;")
        except sqlite3.Error:
            conn.rollback()
            raise
        version = number
    return version
