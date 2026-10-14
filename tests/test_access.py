import asyncio

from vorsa.config import _parse_ids
from vorsa.services.users import get_active_user, sync_owners


def run(coro):
    return asyncio.run(coro)


def test_stranger_gets_their_id_and_no_panel(tg):
    tg.as_stranger(555)
    run(tg.send("/start"))
    assert len(tg.calls) == 1
    text = tg.texts()[0]
    assert "🔒" in text and "<code>555</code>" in text
    assert "Panel Utama" not in text


def test_stranger_button_press_is_refused(tg):
    tg.as_stranger(555)
    run(tg.press("panel:news"))
    (call,) = tg.calls
    assert type(call).__name__ == "AnswerCallbackQuery"
    assert call.text == "🔒 Akses ditolak" and call.show_alert


def test_stranger_in_group_is_ignored_silently(tg):
    from aiogram.types import Chat

    tg.as_stranger(555)
    tg.chat = Chat(id=-100, type="group")
    run(tg.send("/start"))
    assert tg.calls == []


def test_owner_passes_and_name_is_remembered(db, tg):
    run(tg.send("/start"))
    assert "VORSA · Panel Utama" in tg.texts()[0]
    assert get_active_user(db, 1)["name"] == "Wildan"


def test_removed_owner_loses_access(db, tg):
    sync_owners(db, ("2",))
    run(tg.send("/start"))
    assert "🔒" in tg.texts()[0]


def test_sync_owners(db):
    sync_owners(db, ("10", "20"))
    db.execute("INSERT INTO users (telegram_id, role) VALUES ('30', 'admin')")
    sync_owners(db, ("20",))
    assert get_active_user(db, "10") is None  # owner dicabut
    assert get_active_user(db, "20")["role"] == "owner"
    assert get_active_user(db, "30")["role"] == "admin"  # admin tidak disentuh
    sync_owners(db, ())
    assert get_active_user(db, "20") is None
    sync_owners(db, ("10",))
    assert get_active_user(db, "10") is not None  # bisa diaktifkan lagi


def test_parse_ids():
    assert _parse_ids(" 123, 456 ,abc,,123") == ("123", "456")
    assert _parse_ids("") == ()
