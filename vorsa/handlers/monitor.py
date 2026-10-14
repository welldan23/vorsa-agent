"""Handler hub Pantau Berita: kategori dan laporan pengecekan terakhir."""

import sqlite3

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from vorsa.handlers.common import edit_view
from vorsa.keyboards.monitor import (
    CategoryToggle,
    MonitorAction,
    categories_keyboard,
    last_check_keyboard,
)
from vorsa.services.categories import get_categories, toggle_category
from vorsa.stub.mock_data import get_last_check_run
from vorsa.ui.categories import render_category_list
from vorsa.ui.check_run import render_check_run

router = Router(name="monitor")


@router.message(Command("kategori"))
async def show_categories(message: Message, db: sqlite3.Connection) -> None:
    items = get_categories(db)
    await message.answer(render_category_list(items), reply_markup=categories_keyboard(items))


@router.callback_query(MonitorAction.filter(F.action == "categories"))
async def categories_from_hub(query: CallbackQuery, db: sqlite3.Connection) -> None:
    items = get_categories(db)
    await edit_view(query, render_category_list(items), categories_keyboard(items))
    await query.answer()


@router.callback_query(CategoryToggle.filter())
async def toggle(
    query: CallbackQuery, callback_data: CategoryToggle, db: sqlite3.Connection, user: sqlite3.Row
) -> None:
    changed = toggle_category(db, callback_data.id, user_id=user["id"])
    if changed is None:
        await query.answer("Kategori tidak ditemukan", show_alert=True)
        return
    items = get_categories(db)
    await edit_view(query, render_category_list(items), categories_keyboard(items))
    await query.answer(f"{changed.name} {'dinyalakan ✅' if changed.enabled else 'dimatikan ⏸'}")


@router.callback_query(MonitorAction.filter(F.action == "last_check"))
async def last_check(query: CallbackQuery) -> None:
    await edit_view(query, render_check_run(get_last_check_run()), last_check_keyboard())
    await query.answer()
