import asyncio
import io
from dataclasses import replace

from PIL import Image

from vorsa.stub.samples import sample_design, sample_design_image
from vorsa.ui.design import render_preview_caption


def test_placeholder_image_is_instagram_portrait():
    img = Image.open(io.BytesIO(sample_design_image("EMAS PECAH REKOR")))
    assert img.size == (1080, 1350) and img.format == "PNG"


def test_preview_caption_fits_telegram_limit():
    long = replace(sample_design(), caption="kata " * 500)
    text = render_preview_caption(long)
    assert len(text) <= 1024 and "…" in text
    assert render_preview_caption(sample_design()).startswith("🖼 <b>Pratinjau Desain</b> · versi 3")


def test_preview_button_sends_photo(tg):
    asyncio.run(tg.press("dsg:preview:0"))
    photo = next(c for c in tg.calls if type(c).__name__ == "SendPhoto")
    assert photo.chat_id == 1 and photo.photo.filename == "vorsa-pratinjau.png"
    assert [b.text for b in photo.reply_markup.inline_keyboard[0]] == ["🔁 Buat Ulang", "📝 Caption Lengkap"]

    asyncio.run(tg.press("dsg:open:0"))
    assert "<b>Caption Instagram</b>" in tg.texts()[-1]


def test_version_history(tg):
    asyncio.run(tg.press("dsg:history:0"))
    text = tg.texts()[0]
    assert "<b>v3</b>" in text and "· <b>terbaru</b>" in text
    assert text.index("v3") < text.index("v2") < text.index("v1")
    buttons = [b.text for r in tg.calls[0].reply_markup.inline_keyboard for b in r]
    assert buttons == ["🖼 v3", "🖼 v2", "🖼 v1", "⬅️ Kembali ke Desain"]

    asyncio.run(tg.press("dsg:preview:101"))
    photo = next(c for c in tg.calls if type(c).__name__ == "SendPhoto")
    assert "versi 1" in photo.caption


def test_empty_history():
    from vorsa.ui.design import render_version_history

    assert "Belum ada desain" in render_version_history([])


def test_regenerate_adds_new_version(tg):
    from vorsa.stub.samples import reset_sample_versions

    reset_sample_versions()
    try:
        asyncio.run(tg.press("dsg:regenerate:0"))
        prompt = tg.calls[-1]
        assert "🔁 Minta versi baru</b> (sekarang v3)" in prompt.text
        assert [b.text for r in prompt.reply_markup.inline_keyboard for b in r] == [
            "🎲 Variasi lain", "✂️ Judul lebih singkat", "😄 Lebih santai", "🎩 Lebih formal", "Batal",
        ]

        asyncio.run(tg.press("rgn:0:singkat"))
        *steps, draft = [t for t in tg.texts() if "Minta versi" not in t]
        assert len(steps) == 4
        assert "versi 4" in draft and "EMAS CETAK REKOR!" in draft

        asyncio.run(tg.press("dsg:history:200"))
        history = tg.texts()[-1]
        assert history.index("v4") < history.index("v3")

        asyncio.run(tg.press("rgn:200:ngawur"))  # gaya tidak dikenal
        assert tg.calls[-1].text == "Bagian ini sedang disiapkan 🙏"
    finally:
        reset_sample_versions()
