import asyncio
from datetime import datetime, timedelta

from vorsa.db.timeutil import to_db
from vorsa.services.activity import log_activity


def run(coro):
    return asyncio.run(coro)


def seed(db):
    db.executemany(
        "INSERT INTO categories (id, name, is_enabled) VALUES (?, ?, ?)",
        [(1, "Teknologi & AI", 1), (2, "Tren Internet", 0)],
    )
    db.execute("INSERT INTO rss_sources (id, category_id, url) VALUES (1, 1, 'https://a/rss')")
    db.execute(
        "INSERT INTO check_runs (started_at, finished_at, status) VALUES (?, ?, 'success')",
        (to_db(datetime.now() - timedelta(minutes=5)), to_db(datetime.now() - timedelta(minutes=4))),
    )
    db.execute(
        "INSERT INTO articles (source_id, category_id, title, link, content_hash, is_important)"
        " VALUES (1, 1, 'Emas rekor', 'l1', 'h1', 1)"
    )
    log_activity(db, "design_created", "“Emas rekor”")


def test_start_renders_panel_from_database(db, tg):
    seed(db)
    run(tg.send("/start"))
    text = tg.texts()[0]
    assert "Halo, Wildan!" in text
    assert "🟢 Aktif" in text
    assert "Kategori aktif: 1/2" in text
    assert "1 berita penting hari ini" in text
    assert "Desain dibuat — “Emas rekor”" in text
    keyboard = tg.calls[0].reply_markup.inline_keyboard
    assert keyboard[0][0].text == "📰 Berita Terbaru"


def test_start_on_empty_database(tg):
    run(tg.send("/start"))
    text = tg.texts()[0]
    assert "🔴 Berhenti · cek terakhir belum pernah" in text
    assert "0 berita penting hari ini" in text
    assert "Belum ada aktivitas." in text


def test_panel_command_and_refresh_button_use_same_data(db, tg):
    seed(db)
    run(tg.send("/panel"))
    log_activity(db, "published", "“Emas rekor”")
    run(tg.press("panel:home"))
    sent, edited = tg.texts()
    assert "Desain dibuat" in sent
    assert "Terkirim ke Instagram — “Emas rekor”" in edited
