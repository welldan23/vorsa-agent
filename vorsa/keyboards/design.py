"""Tombol inline untuk chat desain."""

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from vorsa.keyboards.news import ArticleAction


class DesignAction(CallbackData, prefix="dsg"):
    action: str  # preview | regenerate | open
    id: int


def design_keyboard(design_id: int, article_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🖼 Lihat Pratinjau", callback_data=DesignAction(action="preview", id=design_id))
    kb.button(text="🔁 Buat Ulang", callback_data=DesignAction(action="regenerate", id=design_id))
    kb.button(text="⬅️ Kembali ke Berita", callback_data=ArticleAction(action="card", id=article_id))
    kb.adjust(2, 1)
    return kb.as_markup()
