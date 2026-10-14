import asyncio

import pytest

from vorsa.services.activity import log_activity


def run(coro):
    return asyncio.run(coro)


def answers(tg):
    return [(c.text, c.show_alert) for c in tg.calls if type(c).__name__ == "AnswerCallbackQuery"]


@pytest.mark.parametrize(
    ("section", "command", "heading"),
    [
        ("news", "/berita", "📰 Berita Terbaru"),
        ("status", "/status", "📡 Status Pemantauan"),
        ("activity", "/aktivitas", "🕘 Aktivitas Terakhir"),
        ("help", "/bantuan", "❓ Bantuan VORSA"),
        ("monitor", "/pantau", "🛰 Pantau Berita Otomatis"),
    ],
)
def test_button_and_command_open_same_view(tg, section, command, heading):
    run(tg.press(f"panel:{section}"))
    run(tg.send(command))
    edited, sent = tg.texts()
    assert heading in edited
    assert edited == sent
    assert tg.calls[0].link_preview_options.is_disabled


def test_help_alias(tg):
    run(tg.send("/help"))
    assert "❓ Bantuan VORSA" in tg.texts()[0]


def test_views_read_database(db, tg):
    log_activity(db, "published", "“Bank sentral tahan suku bunga”")
    run(tg.press("panel:activity"))
    assert "Terkirim ke Instagram — “Bank sentral tahan suku bunga”" in tg.texts()[0]

    run(tg.press("panel:news"))
    assert "Belum ada berita penting" in tg.texts()[1]


def test_section_without_view_falls_back(tg):
    run(tg.press("panel:settings"))
    run(tg.send("/pengaturan"))
    assert answers(tg) == [("Bagian ini sedang disiapkan 🙏", True)]
    assert "⚙️ Pengaturan" in tg.texts()[0]


def test_hub_commands_still_reach_their_router(tg):
    run(tg.send("/kategori"))
    assert "🗂 Kategori Berita" in tg.texts()[0]
