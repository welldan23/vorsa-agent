from datetime import datetime, timezone

from vorsa.services.dedup import content_hash, normalize_link, store_entries
from vorsa.services.fetcher import FeedEntry


def entry(title, link, published=None):
    return FeedEntry(title=title, link=link, summary="ringkas", published_at=published)


def seed(db):
    db.execute("INSERT INTO categories (id, name) VALUES (1, 'Berita Nasional')")
    db.executemany(
        "INSERT INTO rss_sources (id, category_id, url) VALUES (?, 1, ?)",
        [(1, "https://a/rss"), (2, "https://b/rss")],
    )


def test_normalize_link():
    assert normalize_link("HTTPS://WWW.Kompas.com/berita/1/?utm_source=x&id=5&fbclid=y#atas") == (
        "https://kompas.com/berita/1?id=5"
    )
    assert normalize_link("https://kompas.com") == "https://kompas.com/"


def test_title_hash_ignores_case_punctuation_and_spacing():
    assert content_hash("Harga Emas Tembus Rekor!") == content_hash("  harga emas — tembus   rekor ")
    assert content_hash("Harga emas turun") != content_hash("Harga emas naik")


def test_store_skips_duplicates_within_and_across_runs(db):
    seed(db)
    published = datetime(2026, 10, 14, 4, 0, tzinfo=timezone.utc)
    first = store_entries(
        db,
        1,
        1,
        [
            entry("Harga emas tembus rekor", "https://a.id/emas?utm_source=rss", published),
            entry("Harga Emas Tembus Rekor!", "https://a.id/emas-2"),  # judul sama
            entry("DPR sahkan RUU", "https://a.id/ruu"),
            entry("DPR sahkan RUU (update)", "https://www.a.id/ruu/"),  # link sama
        ],
    )
    assert (first.new, first.duplicates) == (2, 2)

    # putaran berikutnya + sumber lain memuat berita yang sama
    second = store_entries(
        db, 2, 1, [entry("harga emas tembus rekor", "https://b.id/emas"), entry("Berita baru", "https://b.id/baru")]
    )
    assert (second.new, second.duplicates) == (1, 1)

    rows = db.execute("SELECT title, link, published_at, source_id FROM articles ORDER BY id").fetchall()
    assert [r["title"] for r in rows] == ["Harga emas tembus rekor", "DPR sahkan RUU", "Berita baru"]
    assert rows[0]["link"] == "https://a.id/emas"
    assert rows[0]["published_at"] == "2026-10-14 04:00:00"
    assert rows[1]["published_at"] is None


def test_store_empty(db):
    seed(db)
    assert store_entries(db, 1, 1, []) == store_entries(db, 1, 1, [])


def test_feed_with_one_link_for_all_entries(db):
    """Google Trends memberi link feed yang sama untuk setiap tren."""
    seed(db)
    feed_link = "https://trends.google.com/trending/rss?geo=ID"
    batch = [entry("sarwendah tan", feed_link), entry("ray dalio", feed_link), entry("jadwal persib", feed_link)]

    assert store_entries(db, 1, 1, batch).new == 3
    links = [r[0] for r in db.execute("SELECT link FROM articles")]
    assert len(set(links)) == 3 and all(link.startswith(feed_link + "#") for link in links)

    # putaran berikutnya: tren lama kembar, tren baru masuk
    again = store_entries(db, 1, 1, [entry("ray dalio", feed_link), entry("timnas", feed_link)])
    assert (again.new, again.duplicates) == (1, 1)


def test_same_link_same_title_in_one_batch_is_still_duplicate(db):
    seed(db)
    batch = [entry("Emas naik", "https://a.id/emas"), entry("Emas naik", "https://a.id/emas")]
    assert store_entries(db, 1, 1, batch).duplicates == 1


def test_homepage_link_is_not_an_identity(db):
    seed(db)
    batch = [entry("Satu", "https://situs.id/"), entry("Dua", "https://situs.id")]
    assert store_entries(db, 1, 1, batch).new == 2
