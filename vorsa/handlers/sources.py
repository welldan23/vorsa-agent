"""Handler kelola sumber RSS: pilih kategori → lihat, tambah, hapus sumber."""

import sqlite3
from html import escape
from urllib.parse import urlparse

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from vorsa.handlers.common import edit_view
from vorsa.keyboards.monitor import (
    MonitorAction,
    SourceAction,
    add_cancel_keyboard,
    delete_confirm_keyboard,
    source_categories_keyboard,
    source_list_keyboard,
)
from vorsa.services import fetcher
from vorsa.services.categories import get_categories, get_category
from vorsa.services.sources import add_source, delete_source, find_source_by_url, get_source, get_sources
from vorsa.ui.sources import (
    render_add_prompt,
    render_delete_confirm,
    render_source_categories,
    render_source_list,
)

router = Router(name="sources")


class AddSource(StatesGroup):
    waiting_url = State()


def is_valid_feed_url(text: str) -> bool:
    parsed = urlparse(text)
    return parsed.scheme in ("http", "https") and "." in parsed.netloc and " " not in text


def _list_view(db: sqlite3.Connection, category_id: int):
    category = get_category(db, category_id)
    sources = get_sources(db, category_id)
    return render_source_list(category, sources), source_list_keyboard(category_id, sources)


@router.message(Command("sumber"))
async def show_source_categories(message: Message, state: FSMContext, db: sqlite3.Connection) -> None:
    await state.clear()
    categories = get_categories(db)
    await message.answer(render_source_categories(categories), reply_markup=source_categories_keyboard(categories))


@router.callback_query(MonitorAction.filter(F.action == "sources"))
async def source_categories_from_hub(query: CallbackQuery, state: FSMContext, db: sqlite3.Connection) -> None:
    await state.clear()
    categories = get_categories(db)
    await edit_view(query, render_source_categories(categories), source_categories_keyboard(categories))
    await query.answer()


@router.callback_query(SourceAction.filter(F.action == "list"))
async def show_sources(
    query: CallbackQuery, callback_data: SourceAction, state: FSMContext, db: sqlite3.Connection
) -> None:
    await state.clear()
    if get_category(db, callback_data.cat) is None:
        await query.answer("Kategori tidak ditemukan", show_alert=True)
        return
    await edit_view(query, *_list_view(db, callback_data.cat))
    await query.answer()


@router.callback_query(SourceAction.filter(F.action == "add"))
async def ask_source_url(
    query: CallbackQuery, callback_data: SourceAction, state: FSMContext, db: sqlite3.Connection
) -> None:
    category = get_category(db, callback_data.cat)
    if category is None:
        await query.answer("Kategori tidak ditemukan", show_alert=True)
        return
    await state.set_state(AddSource.waiting_url)
    await state.update_data(category_id=category.id)
    await edit_view(query, render_add_prompt(category), add_cancel_keyboard(category.id))
    await query.answer()


@router.message(StateFilter(AddSource.waiting_url), Command("batal"))
async def cancel_add(message: Message, state: FSMContext, db: sqlite3.Connection) -> None:
    category_id = (await state.get_data())["category_id"]
    await state.clear()
    text, kb = _list_view(db, category_id)
    await message.answer(f"Dibatalkan.\n\n{text}", reply_markup=kb)


@router.message(StateFilter(AddSource.waiting_url), F.text, ~F.text.startswith("/"))
async def receive_source_url(
    message: Message, state: FSMContext, db: sqlite3.Connection, user: sqlite3.Row
) -> None:
    url = message.text.strip()
    category_id = (await state.get_data())["category_id"]
    if not is_valid_feed_url(url):
        await message.answer(
            "Itu belum terlihat seperti URL 🤔 Kirim yang diawali <code>https://</code>, atau /batal.",
            reply_markup=add_cancel_keyboard(category_id),
        )
        return
    if find_source_by_url(db, url) is not None:
        await message.answer(
            "URL itu sudah terdaftar. Kirim URL lain, atau /batal.",
            reply_markup=add_cancel_keyboard(category_id),
        )
        return

    # Coba ambil dulu supaya salah ketik/bukan feed ketahuan sekarang, bukan 15 menit lagi.
    (result,) = await fetcher.fetch_all([(0, url)])
    if not result.ok:
        await message.answer(
            f"Feed belum bisa dibaca: <b>{escape(result.error)}</b>.\nCek lagi URL-nya, kirim URL lain, atau /batal.",
            reply_markup=add_cancel_keyboard(category_id),
        )
        return
    if add_source(db, category_id, url, user_id=user["id"]) is None:  # keduluan disimpan
        await message.answer("URL itu sudah terdaftar.", reply_markup=add_cancel_keyboard(category_id))
        return

    await state.clear()
    text, kb = _list_view(db, category_id)
    await message.answer(
        f"✅ Sumber ditambahkan — {len(result.entries)} berita terbaca.\n"
        "Berita barunya ikut dipantau mulai pengecekan berikutnya.\n\n" + text,
        reply_markup=kb,
    )


@router.callback_query(SourceAction.filter(F.action == "del"))
async def confirm_delete(query: CallbackQuery, callback_data: SourceAction, db: sqlite3.Connection) -> None:
    source = get_source(db, callback_data.src)
    if source is None:
        await query.answer("Sumber sudah tidak ada", show_alert=True)
        await edit_view(query, *_list_view(db, callback_data.cat))
        return
    await edit_view(query, render_delete_confirm(source), delete_confirm_keyboard(source))
    await query.answer()


@router.callback_query(SourceAction.filter(F.action == "del_ok"))
async def delete(
    query: CallbackQuery, callback_data: SourceAction, db: sqlite3.Connection, user: sqlite3.Row
) -> None:
    removed = delete_source(db, callback_data.src, user_id=user["id"])
    await edit_view(query, *_list_view(db, removed.category_id if removed else callback_data.cat))
    await query.answer("Sumber dihapus 🗑" if removed else "Sumber sudah tidak ada")
