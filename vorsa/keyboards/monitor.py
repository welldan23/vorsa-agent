"""Tombol inline untuk hub Pantau Berita."""

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from vorsa.keyboards.panel import PanelAction
from vorsa.ui.categories import CategoryItem
from vorsa.ui.sources import RssSourceItem, short_url


class MonitorAction(CallbackData, prefix="mon"):
    action: str


class CategoryToggle(CallbackData, prefix="cat"):
    id: int


def monitor_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⏱ Cek Sekarang", callback_data=MonitorAction(action="check_now"))
    kb.button(text="🗂 Kategori", callback_data=MonitorAction(action="categories"))
    kb.button(text="🔗 Sumber RSS", callback_data=MonitorAction(action="sources"))
    kb.button(text="🧾 Cek Terakhir", callback_data=MonitorAction(action="last_check"))
    kb.button(text="🔄 Segarkan", callback_data=PanelAction(section="monitor"))
    kb.button(text="⬅️ Panel Utama", callback_data=PanelAction(section="home"))
    kb.adjust(2)
    return kb.as_markup()


def last_check_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Segarkan", callback_data=MonitorAction(action="last_check"))
    kb.button(text="⬅️ Pantau Berita", callback_data=PanelAction(section="monitor"))
    kb.adjust(2)
    return kb.as_markup()


def categories_keyboard(items: list[CategoryItem]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for c in items:
        kb.button(text=f"{'✅' if c.enabled else '⏸'} {c.name}", callback_data=CategoryToggle(id=c.id))
    kb.button(text="⬅️ Pantau Berita", callback_data=PanelAction(section="monitor"))
    kb.adjust(1)
    return kb.as_markup()


class SourceAction(CallbackData, prefix="src"):
    action: str  # list | add | del | del_ok
    cat: int = 0
    src: int = 0


def source_categories_keyboard(categories: list[CategoryItem]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for c in categories:
        kb.button(text=f"{c.name} ({c.source_count})", callback_data=SourceAction(action="list", cat=c.id))
    kb.button(text="⬅️ Pantau Berita", callback_data=PanelAction(section="monitor"))
    kb.adjust(1)
    return kb.as_markup()


def source_list_keyboard(category_id: int, sources: list[RssSourceItem]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for src in sources:
        kb.button(text=f"🗑 {short_url(src.url)}", callback_data=SourceAction(action="del", cat=category_id, src=src.id))
    kb.button(text="➕ Tambah Sumber", callback_data=SourceAction(action="add", cat=category_id))
    kb.button(text="⬅️ Pilih Kategori", callback_data=MonitorAction(action="sources"))
    kb.adjust(1)
    return kb.as_markup()


def delete_confirm_keyboard(src: RssSourceItem) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🗑 Ya, hapus", callback_data=SourceAction(action="del_ok", cat=src.category_id, src=src.id))
    kb.button(text="Batal", callback_data=SourceAction(action="list", cat=src.category_id))
    kb.adjust(2)
    return kb.as_markup()


def add_cancel_keyboard(category_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Batal", callback_data=SourceAction(action="list", cat=category_id))
    return kb.as_markup()
