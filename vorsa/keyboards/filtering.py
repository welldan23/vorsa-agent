"""Tombol inline menu tingkat penyaringan."""

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from vorsa.keyboards.panel import PanelAction
from vorsa.services.filtering import PRESETS
from vorsa.ui.categories import CategoryItem

PRESET_ICONS = {"longgar": "🟢", "normal": "🟡", "ketat": "🔴"}


class FilterAction(CallbackData, prefix="flt"):
    action: str  # preset | dec | inc | noop
    preset: str = ""
    cat: int = 0


def filter_keyboard(categories: list[CategoryItem], active_preset: str | None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for name, value in PRESETS.items():
        mark = "✓ " if name == active_preset else ""
        kb.button(
            text=f"{mark}{PRESET_ICONS[name]} {name.capitalize()} {value:.0%}",
            callback_data=FilterAction(action="preset", preset=name),
        )
    for c in categories:
        kb.button(text="➖", callback_data=FilterAction(action="dec", cat=c.id))
        kb.button(text=f"{c.name} {c.min_relevance:.0%}", callback_data=FilterAction(action="noop", cat=c.id))
        kb.button(text="➕", callback_data=FilterAction(action="inc", cat=c.id))
    kb.button(text="⬅️ Panel Utama", callback_data=PanelAction(section="home"))
    kb.adjust(3, *([3] * len(categories)), 1)
    return kb.as_markup()
