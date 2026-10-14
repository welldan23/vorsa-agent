import asyncio

import pytest

from vorsa.services.categories import get_categories, toggle_category


def run(coro):
    return asyncio.run(coro)


@pytest.fixture
def seeded(db):
    db.executemany(
        "INSERT INTO categories (id, name, is_enabled, min_relevance) VALUES (?, ?, ?, ?)",
        [(1, "Teknologi & AI", 1, 0.7), (2, "Tren Internet", 0, 0.6)],
    )
    db.executemany(
        "INSERT INTO rss_sources (category_id, url, is_active) VALUES (?, ?, ?)",
        [(1, "https://a/rss", 1), (1, "https://b/rss", 1), (1, "https://c/rss", 0)],
    )
    return db


def test_get_categories(seeded):
    tech, tren = get_categories(seeded)
    assert (tech.name, tech.enabled, tech.min_relevance, tech.source_count) == ("Teknologi & AI", True, 0.7, 2)
    assert (tren.enabled, tren.source_count) == (False, 0)


def test_toggle_persists_and_logs(seeded):
    assert toggle_category(seeded, 1, user_id=None).enabled is False
    assert seeded.execute("SELECT is_enabled FROM categories WHERE id = 1").fetchone()[0] == 0
    assert toggle_category(seeded, 1).enabled is True
    details = [r[0] for r in seeded.execute("SELECT detail FROM activity_logs ORDER BY id")]
    assert details == ["Teknologi & AI dimatikan", "Teknologi & AI dinyalakan"]
    assert toggle_category(seeded, 99) is None


def test_toggle_button_saves_to_database(seeded, tg):
    run(tg.send("/kategori"))
    assert "2 sumber · ambang 70%" in tg.texts()[0]

    run(tg.press("cat:2"))
    assert seeded.execute("SELECT is_enabled FROM categories WHERE id = 2").fetchone()[0] == 1
    assert "2/2 kategori dipantau" in tg.texts()[1]
    toast = next(c.text for c in tg.calls if type(c).__name__ == "AnswerCallbackQuery")
    assert toast == "Tren Internet dinyalakan ✅"

    log = seeded.execute("SELECT a.action, u.telegram_id FROM activity_logs a JOIN users u ON u.id = a.user_id").fetchone()
    assert (log["action"], log["telegram_id"]) == ("category_toggled", "1")


def test_toggle_shows_up_in_status_and_activity(seeded, tg):
    run(tg.press("cat:1"))
    run(tg.press("panel:status"))
    run(tg.press("panel:activity"))
    status, activity = tg.texts()[1:]
    assert "⏸ Teknologi &amp; AI — nonaktif" in status
    assert "🗂 Kategori diubah — Teknologi &amp; AI dimatikan" in activity


def test_toggle_unknown_category(tg):
    run(tg.press("cat:99"))
    (call,) = tg.calls
    assert call.text == "Kategori tidak ditemukan" and call.show_alert
