"""Service kategori berita (tabel categories)."""

import sqlite3

from vorsa.services.activity import log_activity
from vorsa.ui.categories import CategoryItem

_SELECT = """
    SELECT c.id, c.name, c.is_enabled, c.min_relevance,
           (SELECT COUNT(*) FROM rss_sources s WHERE s.category_id = c.id AND s.is_active = 1) AS sources
    FROM categories c
"""


def _item(row: sqlite3.Row) -> CategoryItem:
    return CategoryItem(
        id=row["id"],
        name=row["name"],
        enabled=bool(row["is_enabled"]),
        min_relevance=row["min_relevance"],
        source_count=row["sources"],
    )


def get_categories(conn: sqlite3.Connection) -> list[CategoryItem]:
    return [_item(r) for r in conn.execute(f"{_SELECT} ORDER BY c.id")]


def get_category(conn: sqlite3.Connection, category_id: int) -> CategoryItem | None:
    row = conn.execute(f"{_SELECT} WHERE c.id = ?", (category_id,)).fetchone()
    return _item(row) if row else None


def toggle_category(
    conn: sqlite3.Connection, category_id: int, user_id: int | None = None
) -> CategoryItem | None:
    """Balik status aktif kategori dan catat di activity_logs. None kalau tidak ada."""
    with conn:
        cur = conn.execute("UPDATE categories SET is_enabled = 1 - is_enabled WHERE id = ?", (category_id,))
    if cur.rowcount == 0:
        return None
    category = get_category(conn, category_id)
    log_activity(
        conn,
        "category_toggled",
        f"{category.name} {'dinyalakan' if category.enabled else 'dimatikan'}",
        user_id=user_id,
    )
    return category
