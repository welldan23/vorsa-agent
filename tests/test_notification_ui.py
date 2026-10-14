import asyncio
from dataclasses import replace

from vorsa.keyboards.news import notification_keyboard
from vorsa.stub.samples import sample_notification
from vorsa.ui.notification import render_notification


def test_render_notification():
    n = sample_notification()
    text = render_notification(n)
    assert text.startswith("🔔 <b>Berita Penting</b> · 🔥 91%")
    assert "<b>Harga emas tembus rekor baru" in text
    assert "Ekonomi &amp; Bisnis · cnbcindonesia.com ·" in text
    assert "💡 <i>Kenapa penting:" in text

    bare = render_notification(replace(n, summary="x" * 400, reason=None, published_at=None))
    assert "Kenapa penting" not in bare and "x" * 299 + "…" in bare


def test_keyboard_switches_when_flagged():
    n = sample_notification()
    rows = notification_keyboard(n).inline_keyboard
    assert [b.text for b in rows[0]] == ["📌 Tandai untuk Diolah", "🔗 Baca"]
    assert rows[0][1].url == n.link
    assert [b.text for b in rows[1]] == ["📊 Detail Skor", "🙈 Abaikan"]

    flagged = replace(n, is_flagged=True)
    assert notification_keyboard(flagged).inline_keyboard[0][0].text == "↩️ Batal Tandai"
    assert "Sudah ditandai" in render_notification(flagged)


def test_demo_command(tg):
    asyncio.run(tg.send("/contoh_notif"))
    assert "🔔 <b>Berita Penting</b>" in tg.texts()[0]
    asyncio.run(tg.press("art:flag:0"))
    assert tg.calls[-1].text == "Bagian ini sedang disiapkan 🙏"
