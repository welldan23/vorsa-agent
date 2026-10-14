"""Tombol inline untuk chat desain."""

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from vorsa.keyboards.news import ArticleAction
from vorsa.ui.design import DesignDraft


class DesignAction(CallbackData, prefix="dsg"):
    action: str  # preview | regenerate | open (kembali ke chat desain) | history
    id: int


def design_keyboard(design_id: int, article_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🖼 Lihat Pratinjau", callback_data=DesignAction(action="preview", id=design_id))
    kb.button(text="🔁 Buat Ulang", callback_data=DesignAction(action="regenerate", id=design_id))
    kb.button(text="🕘 Riwayat Versi", callback_data=DesignAction(action="history", id=design_id))
    kb.button(text="⬅️ Kembali ke Berita", callback_data=ArticleAction(action="card", id=article_id))
    kb.adjust(2, 2)
    return kb.as_markup()


def preview_keyboard(design_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔁 Buat Ulang", callback_data=DesignAction(action="regenerate", id=design_id))
    kb.button(text="📝 Caption Lengkap", callback_data=DesignAction(action="open", id=design_id))
    kb.adjust(2)
    return kb.as_markup()


def history_keyboard(versions: list[DesignDraft], back_design_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for d in versions:
        kb.button(text=f"🖼 v{d.version}", callback_data=DesignAction(action="preview", id=d.id))
    kb.button(text="⬅️ Kembali ke Desain", callback_data=DesignAction(action="open", id=back_design_id))
    kb.adjust(*([min(len(versions), 4)] if versions else []), 1)
    return kb.as_markup()


# gaya versi baru → label tombol
REGEN_STYLES = {
    "variasi": "🎲 Variasi lain",
    "singkat": "✂️ Judul lebih singkat",
    "santai": "😄 Lebih santai",
    "formal": "🎩 Lebih formal",
}


class RegenAction(CallbackData, prefix="rgn"):
    id: int  # desain yang mau dibuatkan versi baru
    style: str


def regenerate_keyboard(design_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for style, label in REGEN_STYLES.items():
        kb.button(text=label, callback_data=RegenAction(id=design_id, style=style))
    kb.button(text="Batal", callback_data=DesignAction(action="open", id=design_id))
    kb.adjust(2, 2, 1)
    return kb.as_markup()
