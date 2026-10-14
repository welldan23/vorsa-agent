"""Satpam akses: hanya pengguna aktif di tabel users yang boleh memakai bot."""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from vorsa.services.users import get_active_user, remember_name

log = logging.getLogger(__name__)


def denied_text(telegram_id: int) -> str:
    return (
        "🔒 Maaf, VORSA hanya bisa dipakai pemilik terdaftar.\n\n"
        f"ID Telegram kamu: <code>{telegram_id}</code>\n"
        "Kalau ini bot milikmu, tambahkan ID itu ke <code>OWNER_TELEGRAM_IDS</code> di file .env "
        "lalu nyalakan ulang bot."
    )


class AccessMiddleware(BaseMiddleware):
    """Dipasang sebagai outer middleware di message & callback_query.

    Pengguna yang lolos tersedia di handler sebagai parameter `user` (baris tabel users).
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        sender = getattr(event, "from_user", None)
        if sender is None:  # mis. pesan channel — abaikan
            return None

        user = get_active_user(data["db"], sender.id)
        if user is None:
            log.warning("Akses ditolak untuk Telegram ID %s", sender.id)
            if isinstance(event, CallbackQuery):
                await event.answer("🔒 Akses ditolak", show_alert=True)
            elif isinstance(event, Message) and event.chat.type == "private":
                await event.answer(denied_text(sender.id))
            return None

        remember_name(data["db"], user["id"], sender.first_name)
        data["user"] = user
        return await handler(event, data)
