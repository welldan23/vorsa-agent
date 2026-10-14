from vorsa.db.connection import connect
from vorsa.db.migrate import apply_migrations

PRD_CATEGORIES = [
    "Teknologi & AI",
    "Ekonomi & Bisnis",
    "Berita Nasional",
    "Culture & Entertainment",
    "Berita Internasional",
    "Musik & Lifestyle",
    "Tren Internet",
]


def test_fresh_database_has_prd_categories_with_sources():
    conn = connect(":memory:")
    apply_migrations(conn)
    rows = conn.execute(
        """
        SELECT c.name, c.is_enabled, COUNT(s.id) AS sources
        FROM categories c LEFT JOIN rss_sources s ON s.category_id = c.id AND s.is_active = 1
        GROUP BY c.id ORDER BY c.id
        """
    ).fetchall()
    assert [r["name"] for r in rows] == PRD_CATEGORIES
    assert all(r["is_enabled"] == 1 and r["sources"] >= 1 for r in rows)
    assert all(
        url.startswith("https://") for (url,) in conn.execute("SELECT url FROM rss_sources")
    )
