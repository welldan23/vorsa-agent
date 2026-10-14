"""Handler hub Pantau Berita: kategori, laporan pengecekan terakhir, dan cek manual."""

import sqlite3

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from vorsa.config import Settings
from vorsa.handlers.common import edit_view
from vorsa.keyboards.monitor import (
    CategoryToggle,
    MonitorAction,
    categories_keyboard,
    last_check_keyboard,
)
from vorsa.services.categories import get_categories, toggle_category
from vorsa.services.check_report import count_sources_to_check, get_last_check_report
from vorsa.services.check_run import is_check_running, run_check
from vorsa.ui.categories import render_category_list
from vorsa.ui.check_run import render_check_in_progress, render_check_run

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


def _report(db: sqlite3.Connection, settings: Settings) -> str:
    return render_check_run(get_last_check_report(db, settings.check_interval_minutes))


@router.callback_query(MonitorAction.filter(F.action == "last_check"))
async def last_check(query: CallbackQuery, db: sqlite3.Connection, settings: Settings) -> None:
    await edit_view(query, _report(db, settings), last_check_keyboard())
    await query.answer()


@router.callback_query(MonitorAction.filter(F.action == "check_now"))
async def check_now(query: CallbackQuery, db: sqlite3.Connection, settings: Settings) -> None:
    if is_check_running():
        await query.answer("Pengecekan lain sedang berjalan — tunggu sebentar lalu buka 🧾 Cek Terakhir.", show_alert=True)
        return
    await query.answer("⏱ Mulai mengecek…")
    await edit_view(query, render_check_in_progress(count_sources_to_check(db)), None)
    await run_check(db)
    await edit_view(query, _report(db, settings), last_check_keyboard())
