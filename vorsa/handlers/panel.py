"""Handler Panel Utama: /start, /panel, dan router tombol/perintah menu.

Setiap section menu punya satu fungsi tampilan di SECTION_VIEWS. Tombol inline
(PanelAction) dan perintah slash (MenuItem.command) sama-sama diarahkan ke sana.
Section yang belum punya tampilan jatuh ke router fallback.
"""

import sqlite3
from collections.abc import Callable

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from vorsa.config import Settings
from vorsa.handlers.common import NO_PREVIEW, EditResult, edit_view
from vorsa.keyboards.monitor import monitor_keyboard
from vorsa.keyboards.panel import (
    PanelAction,
    back_to_panel_keyboard,
    main_panel_keyboard,
    section_keyboard,
)
from vorsa.menu import MENU_ITEMS, PANEL_COMMAND
from vorsa.services.activity import get_recent_activity
from vorsa.services.check_report import get_monitor_overview
from vorsa.services.monitoring import get_monitoring_status
from vorsa.services.news import get_important_articles
from vorsa.services.panel import get_panel_snapshot
from vorsa.ui.activity import render_activity_list
from vorsa.ui.help import render_help
from vorsa.ui.monitor import render_monitor_overview
from vorsa.ui.news import render_news_summary
from vorsa.ui.panel import render_main_panel
from vorsa.ui.status import render_monitoring_status

router = Router(name="panel")

View = tuple[str, InlineKeyboardMarkup]

SECTION_VIEWS: dict[str, Callable[[sqlite3.Connection, Settings], View]] = {
    "news": lambda db, s: (render_news_summary(get_important_articles(db)), section_keyboard("news")),
    "status": lambda db, s: (
        render_monitoring_status(get_monitoring_status(db, s.check_interval_minutes)),
        section_keyboard("status"),
    ),
    "activity": lambda db, s: (render_activity_list(get_recent_activity(db)), section_keyboard("activity")),
    "help": lambda db, s: (render_help(), back_to_panel_keyboard()),
    "monitor": lambda db, s: (
        render_monitor_overview(get_monitor_overview(db, s.check_interval_minutes)),
        monitor_keyboard(),
    ),
}

# perintah slash → section, diambil dari daftar menu (+ alias /help)
COMMAND_SECTIONS = {i.command: i.section for i in MENU_ITEMS if i.section in SECTION_VIEWS}
COMMAND_SECTIONS["help"] = "help"


def _panel_text(db: sqlite3.Connection, settings: Settings, user_name: str | None) -> str:
    return render_main_panel(get_panel_snapshot(db, settings.check_interval_minutes), user_name)


@router.message(CommandStart())
@router.message(Command(PANEL_COMMAND[0], "menu"))
async def show_panel(message: Message, db: sqlite3.Connection, settings: Settings) -> None:
    name = message.from_user.first_name if message.from_user else None
    await message.answer(_panel_text(db, settings, name), reply_markup=main_panel_keyboard())


@router.message(Command(*COMMAND_SECTIONS))
async def section_command(
    message: Message, command: CommandObject, db: sqlite3.Connection, settings: Settings
) -> None:
    text, keyboard = SECTION_VIEWS[COMMAND_SECTIONS[command.command]](db, settings)
    await message.answer(text, reply_markup=keyboard, link_preview_options=NO_PREVIEW)


@router.callback_query(PanelAction.filter(F.section == "home"))
async def refresh_panel(query: CallbackQuery, db: sqlite3.Connection, settings: Settings) -> None:
    result = await edit_view(query, _panel_text(db, settings, query.from_user.first_name), main_panel_keyboard())
    await query.answer("Panel sudah paling baru ✅" if result is EditResult.UNCHANGED else "Panel diperbarui 🔄")


@router.callback_query(PanelAction.filter(F.section.in_(SECTION_VIEWS)))
async def section_button(
    query: CallbackQuery, callback_data: PanelAction, db: sqlite3.Connection, settings: Settings
) -> None:
    await edit_view(query, *SECTION_VIEWS[callback_data.section](db, settings))
    await query.answer()
