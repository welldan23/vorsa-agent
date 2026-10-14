import asyncio

from aiogram.types import Chat, InaccessibleMessage

from vorsa.services.activity import log_activity


def run(coro):
    return asyncio.run(coro)


def names(tg):
    return [type(c).__name__ for c in tg.calls]


def toast(tg):
    return next(c.text for c in tg.calls if type(c).__name__ == "AnswerCallbackQuery")


def test_refresh_edits_panel_with_latest_data(db, tg):
    log_activity(db, "approved", "“Emas rekor”")
    run(tg.press("panel:home"))
    assert names(tg) == ["EditMessageText", "AnswerCallbackQuery"]
    assert "Disetujui — “Emas rekor”" in tg.texts()[0]
    assert "Diperbarui " in tg.texts()[0]
    assert toast(tg) == "Panel diperbarui 🔄"


def test_refresh_without_changes(tg):
    tg.edit_error = "Bad Request: message is not modified"
    run(tg.press("panel:home"))
    assert names(tg) == ["EditMessageText", "AnswerCallbackQuery"]
    assert toast(tg) == "Panel sudah paling baru ✅"


def test_refresh_resends_when_message_cannot_be_edited(tg):
    tg.edit_error = "Bad Request: message to edit not found"
    run(tg.press("panel:home"))
    assert names(tg) == ["EditMessageText", "SendMessage", "AnswerCallbackQuery"]
    assert "VORSA · Panel Utama" in tg.calls[1].text
    assert tg.calls[1].chat_id == 1


def test_refresh_on_old_inaccessible_message(tg):
    old = InaccessibleMessage(chat=Chat(id=1, type="private"), message_id=2)
    run(tg.press("panel:home", message=old))
    assert names(tg) == ["SendMessage", "AnswerCallbackQuery"]


def test_other_sections_also_resend(tg):
    tg.edit_error = "Bad Request: message can't be edited"
    run(tg.press("panel:status"))
    assert "📡 Status Pemantauan" in tg.texts()[-1]
