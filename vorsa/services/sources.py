"""Service sumber RSS (tabel rss_sources)."""

import sqlite3

from vorsa.db.timeutil import from_db
from vorsa.services.activity import log_activity
from vorsa.ui.sources import RssSourceItem


def _item(row: sqlite3.Row) -> RssSourceItem:
    return RssSourceItem(
        id=row["id"],
        category_id=row["category_id"],
        url=row["url"],
        is_active=bool(row["is_active"]),
        failing=row["last_error"] is not None,
        last_fetched_at=from_db(row["last_fetched_at"]),
    )


def get_sources(conn: sqlite3.Connection, category_id: int) -> list[RssSourceItem]:
    rows = conn.execute("SELECT * FROM rss_sources WHERE category_id = ? ORDER BY id", (category_id,))
    return [_item(r) for r in rows]


def get_source(conn: sqlite3.Connection, source_id: int) -> RssSourceItem | None:
    row = conn.execute("SELECT * FROM rss_sources WHERE id = ?", (source_id,)).fetchone()
    return _item(row) if row else None


def find_source_by_url(conn: sqlite3.Connection, url: str) -> RssSourceItem | None:
    row = conn.execute("SELECT * FROM rss_sources WHERE url = ?", (url,)).fetchone()
    return _item(row) if row else None


def add_source(
    conn: sqlite3.Connection, category_id: int, url: str, user_id: int | None = None
) -> RssSourceItem | None:
    """Tambah sumber aktif. None kalau URL sudah terdaftar (url UNIQUE)."""
    with conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO rss_sources (category_id, url) VALUES (?, ?)", (category_id, url)
        )
    if cur.rowcount == 0:
        return None
    log_activity(conn, "source_added", url, user_id=user_id)
    return get_source(conn, cur.lastrowid)


def delete_source(conn: sqlite3.Connection, source_id: int, user_id: int | None = None) -> RssSourceItem | None:
    """Hapus sumber; berita lamanya tetap tersimpan (source_id jadi NULL)."""
    source = get_source(conn, source_id)
    if source is None:
        return None
    with conn:
        conn.execute("DELETE FROM rss_sources WHERE id = ?", (source_id,))
    log_activity(conn, "source_deleted", source.url, user_id=user_id)
    return source
