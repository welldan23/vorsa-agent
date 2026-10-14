from datetime import datetime, timedelta

from vorsa.db.timeutil import from_db, to_db
from vorsa.services.news import count_important_today, get_important_articles, source_name


def seed(db):
    db.executemany(
        "INSERT INTO categories (id, name, is_enabled) VALUES (?, ?, ?)",
        [(1, "Teknologi & AI", 1), (2, "Tren Internet", 0)],
    )
    db.executemany(
        "INSERT INTO rss_sources (id, category_id, url) VALUES (?, ?, ?)",
        [(1, 1, "https://www.theverge.com/rss/index.xml"), (2, 2, "https://trends.example.com/rss")],
    )


def add_article(db, n, *, important=1, source=1, category=1, published=None, fetched=None, score=0.8):
    db.execute(
        "INSERT INTO articles (source_id, category_id, title, link, content_hash, relevance_score,"
        " is_important, published_at, fetched_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (source, category, f"Berita {n}", f"https://x/{n}", f"h{n}", score, important,
         published, fetched or to_db(datetime.now())),
    )


def test_returns_only_important_from_enabled_categories_newest_first(db):
    seed(db)
    now = datetime.now().replace(microsecond=0)
    add_article(db, 1, published=to_db(now - timedelta(hours=2)))
    add_article(db, 2, published=to_db(now - timedelta(minutes=5)), score=0.93)
    add_article(db, 3, important=0, published=to_db(now))                       # tidak lolos saring
    add_article(db, 4, source=2, category=2, published=to_db(now))              # kategori mati
    add_article(db, 5, published=None, fetched=to_db(now - timedelta(hours=1)))  # tanpa waktu terbit

    articles = get_important_articles(db)

    assert [a.title for a in articles] == ["Berita 2", "Berita 5", "Berita 1"]
    top = articles[0]
    assert top.category == "Teknologi & AI"
    assert top.source == "theverge.com"
    assert top.relevance_score == 0.93
    assert top.published_at == now - timedelta(minutes=5)  # kembali ke waktu lokal


def test_limit_and_empty(db):
    assert get_important_articles(db) == []
    seed(db)
    for n in range(5):
        add_article(db, n)
    assert len(get_important_articles(db, limit=3)) == 3


def test_count_important_today(db):
    seed(db)
    now = datetime.now()
    add_article(db, 1, fetched=to_db(now))
    add_article(db, 2, fetched=to_db(now - timedelta(days=2)))  # kemarin lusa
    add_article(db, 3, important=0, fetched=to_db(now))
    assert count_important_today(db) == 1


def test_helpers():
    assert source_name("https://www.kompas.com/rss") == "kompas.com"
    stamp = datetime(2026, 1, 2, 3, 4, 5)
    assert from_db(to_db(stamp)) == stamp
    assert from_db(None) is None
