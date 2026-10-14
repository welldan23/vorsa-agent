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
    assert render_preview_caption(sample_design()).startswith("🖼 <b>Pratinjau Desain</b> · versi 1")


def test_preview_button_sends_photo(tg):
    asyncio.run(tg.press("dsg:preview:0"))
    photo = next(c for c in tg.calls if type(c).__name__ == "SendPhoto")
    assert photo.chat_id == 1 and photo.photo.filename == "vorsa-pratinjau.png"
    assert [b.text for b in photo.reply_markup.inline_keyboard[0]] == ["🔁 Buat Ulang", "📝 Caption Lengkap"]

    asyncio.run(tg.press("dsg:open:0"))
    assert "<b>Caption Instagram</b>" in tg.texts()[-1]
