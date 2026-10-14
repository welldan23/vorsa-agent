"""Tombol inline untuk Panel Utama."""

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from vorsa.menu import MENU_ITEMS


class PanelAction(CallbackData, prefix="panel"):
    section: str


def main_panel_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for item in (i for i in MENU_ITEMS if i.in_panel):
        kb.button(text=item.label, callback_data=PanelAction(section=item.section))
    kb.button(text="🔄 Segarkan", callback_data=PanelAction(section="home"))
    kb.adjust(2)
    return kb.as_markup()


def back_to_panel_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Panel Utama", callback_data=PanelAction(section="home"))
    return kb.as_markup()


def section_keyboard(section: str) -> InlineKeyboardMarkup:
    """Tombol untuk halaman bagian: segarkan halaman ini + kembali ke panel."""
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Segarkan", callback_data=PanelAction(section=section))
    kb.button(text="⬅️ Panel Utama", callback_data=PanelAction(section="home"))
    kb.adjust(2)
    return kb.as_markup()
