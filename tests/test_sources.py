import asyncio

import pytest

from vorsa.services import fetcher
from vorsa.services.fetcher import FeedEntry, FetchResult
from vorsa.services.news import get_important_articles


def run(coro):
    return asyncio.run(coro)


@pytest.fixture
def seeded(db):
    db.execute("INSERT INTO categories (id, name) VALUES (3, 'Berita Nasional')")
    db.executemany(
        "INSERT INTO rss_sources (id, category_id, url, last_error) VALUES (?, 3, ?, ?)",
        [(1, "https://kompas.com/rss", None), (2, "https://antara.id/rss", "Timeout 10 detik")],
    )
    return db


@pytest.fixture
def feeds(monkeypatch):
    """URL → hasil palsu; URL yang tidak terdaftar dianggap feed valid berisi 3 berita."""
    answers = {}

    async def fetch_all(sources, session=None):
        entry = FeedEntry(title="x", link="https://x", summary="", published_at=None)
        return [answers.get(url) or FetchResult(sid, url, entries=[entry] * 3) for sid, url in sources]

    monkeypatch.setattr(fetcher, "fetch_all", fetch_all)
    return answers


def urls(db):
    return [r[0] for r in db.execute("SELECT url FROM rss_sources ORDER BY id")]


def last_text(tg):
    return tg.texts()[-1]


def test_list_shows_database_state(seeded, tg):
    run(tg.press("src:list:3:0"))
    text = last_text(tg)
    assert "https://kompas.com/rss" in text and "⚠️ gagal diambil" in text


def test_add_source_flow(seeded, tg, feeds):
    run(tg.press("src:add:3:0"))
    run(tg.send("bukan url"))
    assert "belum terlihat seperti URL" in last_text(tg)
    run(tg.send("https://kompas.com/rss"))
    assert "sudah terdaftar" in last_text(tg)

    feeds["https://rusak.id/rss"] = FetchResult(0, "https://rusak.id/rss", error="Bukan feed RSS/Atom yang valid")
    run(tg.send("https://rusak.id/rss"))
    assert "Feed belum bisa dibaca: <b>Bukan feed RSS/Atom yang valid</b>" in last_text(tg)
    assert "https://rusak.id/rss" not in urls(seeded)

    run(tg.send("https://tempo.co/rss"))
    assert "✅ Sumber ditambahkan — 3 berita terbaca" in last_text(tg)
    assert urls(seeded)[-1] == "https://tempo.co/rss"
    log = seeded.execute("SELECT action, detail, user_id FROM activity_logs").fetchone()
    assert (log["action"], log["detail"]) == ("source_added", "https://tempo.co/rss") and log["user_id"]

    run(tg.send("https://lagi.id/rss"))  # sudah keluar dari mode tambah: diabaikan
    assert "https://lagi.id/rss" not in urls(seeded)


def test_cancel_add(seeded, tg, feeds):
    run(tg.press("src:add:3:0"))
    run(tg.send("/batal"))
    assert last_text(tg).startswith("Dibatalkan.")
    run(tg.send("https://tempo.co/rss"))
    assert "https://tempo.co/rss" not in urls(seeded)


def test_delete_source_keeps_articles(seeded, tg):
    seeded.execute(
        "INSERT INTO articles (source_id, category_id, title, link, content_hash, is_important)"
        " VALUES (1, 3, 'Berita lama', 'https://kompas.com/a', 'h', 1)"
    )
    run(tg.press("src:del:3:1"))
    assert "Hapus sumber ini?" in last_text(tg)
    run(tg.press("src:del_ok:3:1"))

    assert urls(seeded) == ["https://antara.id/rss"]
    assert "kompas.com/rss" not in last_text(tg)
    (article,) = get_important_articles(seeded)
    assert (article.title, article.source) == ("Berita lama", "kompas.com")
    assert seeded.execute("SELECT action FROM activity_logs").fetchone()[0] == "source_deleted"

    run(tg.press("src:del_ok:3:1"))  # tombol lama ditekan lagi
    toast = [c.text for c in tg.calls if type(c).__name__ == "AnswerCallbackQuery"][-1]
    assert toast == "Sumber sudah tidak ada"
