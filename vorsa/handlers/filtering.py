"""Handler menu tingkat penyaringan (/saring)."""

import sqlite3

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from vorsa.handlers.common import edit_view
from vorsa.keyboards.filtering import FilterAction, filter_keyboard
from vorsa.keyboards.panel import PanelAction
from vorsa.services.categories import get_categories
from vorsa.services.filtering import STEP, adjust_threshold, apply_preset, current_preset
from vorsa.ui.filtering import render_filter_menu

router = Router(name="filtering")


def filter_view(db: sqlite3.Connection) -> tuple[str, InlineKeyboardMarkup]:
    categories = get_categories(db)
    preset = current_preset([c.min_relevance for c in categories])
    return render_filter_menu(categories, preset), filter_keyboard(categories, preset)


@router.message(Command("saring"))
async def show_filter(message: Message, db: sqlite3.Connection) -> None:
    text, kb = filter_view(db)
    await message.answer(text, reply_markup=kb)


@router.callback_query(PanelAction.filter(F.section == "filter"))
async def filter_from_panel(query: CallbackQuery, db: sqlite3.Connection) -> None:
    await edit_view(query, *filter_view(db))
    await query.answer()


@router.callback_query(FilterAction.filter(F.action == "preset"))
async def choose_preset(
    query: CallbackQuery, callback_data: FilterAction, db: sqlite3.Connection, user: sqlite3.Row
) -> None:
    value = apply_preset(db, callback_data.preset, user_id=user["id"])
    await edit_view(query, *filter_view(db))
    await query.answer(f"Semua kategori diatur ke {value:.0%}")


@router.callback_query(FilterAction.filter(F.action.in_({"dec", "inc"})))
async def adjust(query: CallbackQuery, callback_data: FilterAction, db: sqlite3.Connection, user: sqlite3.Row) -> None:
    delta = STEP if callback_data.action == "inc" else -STEP
    value = adjust_threshold(db, callback_data.cat, delta, user_id=user["id"])
    if value is None:
        await query.answer("Kategori tidak ditemukan", show_alert=True)
        return
    await edit_view(query, *filter_view(db))
    await query.answer(f"Ambang jadi {value:.0%}")


@router.callback_query(FilterAction.filter(F.action == "noop"))
async def noop(query: CallbackQuery) -> None:
    await query.answer("Pakai ➖ / ➕ di sampingnya untuk mengubah ambang")
