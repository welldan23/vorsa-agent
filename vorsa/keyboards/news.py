"""Tombol inline untuk kartu berita/notifikasi."""

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from vorsa.ui.notification import ArticleNotification


class ArticleAction(CallbackData, prefix="art"):
    action: str  # flag | unflag | ignore
    id: int


def notification_keyboard(n: ArticleNotification) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if n.is_flagged:
        kb.button(text="↩️ Batal Tandai", callback_data=ArticleAction(action="unflag", id=n.id))
    else:
        kb.button(text="📌 Tandai untuk Diolah", callback_data=ArticleAction(action="flag", id=n.id))
    kb.button(text="🔗 Baca", url=n.link)
    kb.button(text="🙈 Abaikan", callback_data=ArticleAction(action="ignore", id=n.id))
    kb.adjust(2, 1)
    return kb.as_markup()
