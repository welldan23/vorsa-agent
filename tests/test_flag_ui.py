import asyncio

import pytest

from vorsa.stub.samples import set_sample_flag


def run(coro):
    return asyncio.run(coro)


@pytest.fixture(autouse=True)
def reset_flag():
    set_sample_flag(False)
    yield
    set_sample_flag(False)


def toasts(tg):
    return [c.text for c in tg.calls if type(c).__name__ == "AnswerCallbackQuery"]


def test_flag_then_later_then_unflag(tg):
    run(tg.press("art:flag:0"))
    confirm = tg.calls[0]
    assert "📌 <b>Berita ditandai untuk diolah</b>" in confirm.text
    assert [b.text for r in confirm.reply_markup.inline_keyboard for b in r] == [
        "🎨 Buat Desain Sekarang", "⏰ Nanti Saja", "↩️ Batal Tandai",
    ]

    run(tg.press("art:card:0"))  # nanti saja → kartu tetap bertanda
    card = tg.texts()[-1]
    assert "Sudah ditandai" in card
    assert tg.calls[-2].reply_markup.inline_keyboard[0][0].text == "↩️ Batal Tandai"

    run(tg.press("art:unflag:0"))
    assert "Sudah ditandai" not in tg.texts()[-1]
    assert toasts(tg) == ["📌 Ditandai", None, "Tanda dibatalkan"]


def test_design_button_opens_design_chat(tg):
    run(tg.press("art:design:0"))
    progress, draft = tg.texts()
    assert "Lagi bikin desain VORSA" in progress
    assert "🎨 <b>Desain VORSA</b> · versi 1 · 📝 Draf" in draft
    assert "<b>Caption Instagram</b>" in draft and "#VORSA #emas" in draft
    buttons = [b.text for r in tg.calls[-1].reply_markup.inline_keyboard for b in r]
    assert buttons == ["🖼 Lihat Pratinjau", "🔁 Buat Ulang", "⬅️ Kembali ke Berita"]

    run(tg.press("dsg:preview:0"))
    assert toasts(tg)[-1] == "Bagian ini sedang disiapkan 🙏"
