from datetime import datetime

import pytest
from aiogram.types import CallbackQuery, Chat, Message, Update, User

from vorsa.db.connection import connect
from vorsa.db.migrate import apply_migrations


@pytest.fixture
def db():
    """Database kosong di memori dengan skema terbaru."""
    conn = connect(":memory:")
    apply_migrations(conn)
    yield conn
    conn.close()


_DISPATCHER = None  # router aiogram hanya bisa dipasang sekali, jadi dispatcher dipakai ulang


class FakeTelegram:
    """Jalankan update ke dispatcher tanpa koneksi Telegram; semua panggilan API dicatat."""

    def __init__(self, db, monkeypatch):
        from aiogram import Bot

        from vorsa.bot import create_bot, create_dispatcher
        from vorsa.config import Settings
        from vorsa.services.users import sync_owners

        self.calls = []

        async def fake_call(bot, method, request_timeout=None):
            self.calls.append(method)
            return True

        monkeypatch.setattr(Bot, "__call__", fake_call)
        self.settings = Settings(
            bot_token="123456:TEST", database_path=":memory:", check_interval_minutes=15, owner_telegram_ids=("1",)
        )
        sync_owners(db, self.settings.owner_telegram_ids)  # pengguna tes (id 1) adalah pemilik
        self.bot = create_bot(self.settings.bot_token)
        global _DISPATCHER
        if _DISPATCHER is None:
            _DISPATCHER = create_dispatcher(db, self.settings)
        _DISPATCHER["db"] = db
        _DISPATCHER["settings"] = self.settings
        _DISPATCHER.fsm.storage.storage.clear()  # state FSM tidak bocor antar tes
        self.dp = _DISPATCHER
        self.user = User(id=1, is_bot=False, first_name="Wildan")
        self.chat = Chat(id=1, type="private")

    def as_stranger(self, telegram_id=999):
        """Kirim update berikutnya sebagai orang yang tidak terdaftar."""
        self.user = User(id=telegram_id, is_bot=False, first_name="Orang Asing")
        self.chat = Chat(id=telegram_id, type="private")

    async def send(self, text):
        msg = Message(message_id=1, date=datetime.now(), chat=self.chat, from_user=self.user, text=text)
        await self.dp.feed_update(self.bot, Update(update_id=1, message=msg))

    async def press(self, data):
        old = Message(message_id=2, date=datetime.now(), chat=self.chat, text="old")
        query = CallbackQuery(id="q", from_user=self.user, chat_instance="c", data=data, message=old)
        await self.dp.feed_update(self.bot, Update(update_id=2, callback_query=query))

    def texts(self):
        """Teks pesan yang dikirim/diedit bot (tanpa jawaban tombol)."""
        return [c.text for c in self.calls if type(c).__name__ in ("SendMessage", "EditMessageText")]


@pytest.fixture
def tg(db, monkeypatch):
    return FakeTelegram(db, monkeypatch)
