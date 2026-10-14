"""Service berita yang lolos saring (articles.is_important = 1)."""

import sqlite3
from urllib.parse import urlparse

from vorsa.db.timeutil import from_db, local_midnight_db
from vorsa.ui.news import ArticleSummary

# Berita dari kategori yang dimatikan tidak ditampilkan.
_IMPORTANT = """
    FROM articles a
    JOIN categories c ON c.id = a.category_id
    JOIN rss_sources s ON s.id = a.source_id
    WHERE a.is_important = 1 AND c.is_enabled = 1
"""


def source_name(url: str) -> str:
    """Nama sumber dari URL feed, mis. https://www.kompas.com/rss → kompas.com."""
    return urlparse(url).netloc.removeprefix("www.") or url


def get_important_articles(conn: sqlite3.Connection, limit: int = 50) -> list[ArticleSummary]:
    """Berita penting terbaru dulu (pakai waktu terbit, atau waktu diambil kalau kosong)."""
    rows = conn.execute(
        f"""
        SELECT a.title, a.link, a.relevance_score, c.name AS category, s.url AS source_url,
               COALESCE(a.published_at, a.fetched_at) AS published_at
        {_IMPORTANT}
        ORDER BY COALESCE(a.published_at, a.fetched_at) DESC, a.id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [
        ArticleSummary(
            title=r["title"],
            category=r["category"],
            source=source_name(r["source_url"]),
            link=r["link"],
            relevance_score=r["relevance_score"] or 0.0,
            published_at=from_db(r["published_at"]),
        )
        for r in rows
    ]


def count_important_today(conn: sqlite3.Connection) -> int:
    """Jumlah berita penting yang diambil sejak tengah malam (waktu lokal)."""
    return conn.execute(
        f"SELECT COUNT(*) {_IMPORTANT} AND a.fetched_at >= ?", (local_midnight_db(),)
    ).fetchone()[0]
