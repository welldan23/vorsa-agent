"""Handler hub Pantau Berita: kategori dan laporan pengecekan terakhir."""

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
from vorsa.stub.mock_data import get_categories, get_last_check_run, toggle_category
from vorsa.ui.categories import render_category_list
from vorsa.ui.check_run import render_check_run

router = Router(name="monitor")


@router.message(Command("kategori"))
async def show_categories(message: Message) -> None:
    items = get_categories()
    await message.answer(render_category_list(items), reply_markup=categories_keyboard(items))


@router.callback_query(MonitorAction.filter(F.action == "categories"))
async def categories_from_hub(query: CallbackQuery) -> None:
    items = get_categories()
    await edit_view(query, render_category_list(items), categories_keyboard(items))
    await query.answer()


@router.callback_query(CategoryToggle.filter())
async def toggle(query: CallbackQuery, callback_data: CategoryToggle) -> None:
    changed = toggle_category(callback_data.id)
    if changed is None:
        await query.answer("Kategori tidak ditemukan", show_alert=True)
        return
    items = get_categories()
    await edit_view(query, render_category_list(items), categories_keyboard(items))
    await query.answer(f"{changed.name} {'dinyalakan ✅' if changed.enabled else 'dimatikan ⏸'}")


@router.callback_query(MonitorAction.filter(F.action == "last_check"))
async def last_check(query: CallbackQuery) -> None:
    await edit_view(query, render_check_run(get_last_check_run()), last_check_keyboard())
    await query.answer()
