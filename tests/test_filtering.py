import asyncio

import pytest

from vorsa.services.filtering import adjust_threshold, apply_preset, clamp, current_preset


def run(coro):
    return asyncio.run(coro)


@pytest.fixture
def seeded(db):
    db.executemany(
        "INSERT INTO categories (id, name, min_relevance, is_enabled) VALUES (?, ?, ?, ?)",
        [(1, "Teknologi & AI", 0.7, 1), (2, "Tren Internet", 0.7, 0)],
    )
    return db


def thresholds(db):
    return [r[0] for r in db.execute("SELECT min_relevance FROM categories ORDER BY id")]


def test_presets_and_detection(seeded):
    assert current_preset(thresholds(seeded)) == "normal"
    apply_preset(seeded, "ketat")
    assert thresholds(seeded) == [0.85, 0.85]
    assert current_preset(thresholds(seeded)) == "ketat"
    assert current_preset([0.7, 0.75]) is None
    assert current_preset([0.72]) is None


def test_adjust_clamps_and_logs(seeded):
    assert adjust_threshold(seeded, 1, 0.05) == 0.75
    assert thresholds(seeded) == [0.75, 0.7]
    for _ in range(10):
        adjust_threshold(seeded, 1, 0.05)
    assert thresholds(seeded)[0] == 0.95
    assert adjust_threshold(seeded, 99, 0.05) is None
    assert clamp(0.1) == 0.3
    # tidak mencatat aktivitas kalau sudah mentok
    logs = [r[0] for r in seeded.execute("SELECT detail FROM activity_logs")]
    assert logs[-1] == "Teknologi & AI: 95%" and len(logs) == 5


def test_filter_menu_buttons(seeded, tg):
    run(tg.press("panel:filter"))
    text = tg.texts()[0]
    assert "Mode: <b>Normal</b>" in text and "Tren Internet <i>(nonaktif)</i>" in text
    rows = tg.calls[0].reply_markup.inline_keyboard
    assert [b.text for b in rows[0]] == ["🟢 Longgar 55%", "✓ 🟡 Normal 70%", "🔴 Ketat 85%"]
    assert [b.text for b in rows[1]] == ["➖", "Teknologi & AI 70%", "➕"]

    run(tg.press("flt:inc::1"))
    assert "Mode: <b>Campuran</b>" in tg.texts()[-1]
    run(tg.press("flt:preset:longgar:0"))
    assert thresholds(seeded) == [0.55, 0.55]
    assert "Mode: <b>Longgar</b>" in tg.texts()[-1]
    toasts = [c.text for c in tg.calls if type(c).__name__ == "AnswerCallbackQuery"]
    assert toasts[-2:] == ["Ambang jadi 75%", "Semua kategori diatur ke 55%"]


def test_saring_command(seeded, tg):
    run(tg.send("/saring"))
    assert "🎚 Tingkat Penyaringan" in tg.texts()[0]
