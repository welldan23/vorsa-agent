"""Handler Panel Utama: /start, /panel, menu perintah, dan tombol navigasinya."""

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from vorsa.handlers.common import NO_PREVIEW, edit_view
from vorsa.keyboards.monitor import monitor_keyboard
from vorsa.keyboards.panel import (
    PanelAction,
    back_to_panel_keyboard,
    main_panel_keyboard,
    section_keyboard,
)
from vorsa.menu import PANEL_COMMAND
from vorsa.stub.mock_data import (
    get_important_articles,
    get_monitor_overview,
    get_monitoring_status,
    get_panel_snapshot,
    get_recent_activity,
)
from vorsa.ui.activity import render_activity_list
from vorsa.ui.help import render_help
from vorsa.ui.monitor import render_monitor_overview
from vorsa.ui.news import render_news_summary
from vorsa.ui.panel import render_main_panel
from vorsa.ui.status import render_monitoring_status

router = Router(name="panel")



@router.message(CommandStart())
@router.message(Command(PANEL_COMMAND[0], "menu"))
async def show_panel(message: Message) -> None:
    name = message.from_user.first_name if message.from_user else None
    await message.answer(
        render_main_panel(get_panel_snapshot(), name),
        reply_markup=main_panel_keyboard(),
    )


@router.message(Command("bantuan", "help"))
async def show_help(message: Message) -> None:
    await message.answer(render_help(), reply_markup=back_to_panel_keyboard())


@router.message(Command("berita"))
async def show_news(message: Message) -> None:
    await message.answer(
        render_news_summary(get_important_articles()),
        reply_markup=section_keyboard("news"),
        link_preview_options=NO_PREVIEW,
    )


@router.message(Command("status"))
async def show_status(message: Message) -> None:
    await message.answer(
        render_monitoring_status(get_monitoring_status()),
        reply_markup=section_keyboard("status"),
    )


@router.message(Command("aktivitas"))
async def show_activity(message: Message) -> None:
    await message.answer(
        render_activity_list(get_recent_activity()),
        reply_markup=section_keyboard("activity"),
    )


@router.message(Command("pantau"))
async def show_monitor(message: Message) -> None:
    await message.answer(render_monitor_overview(get_monitor_overview()), reply_markup=monitor_keyboard())


@router.callback_query(PanelAction.filter(F.section == "home"))
async def refresh_panel(query: CallbackQuery) -> None:
    text = render_main_panel(get_panel_snapshot(), query.from_user.first_name)
    await edit_view(query, text, main_panel_keyboard())
    await query.answer("Panel diperbarui")


@router.callback_query(PanelAction.filter(F.section == "help"))
async def help_from_panel(query: CallbackQuery) -> None:
    await edit_view(query, render_help(), back_to_panel_keyboard())
    await query.answer()


@router.callback_query(PanelAction.filter(F.section == "news"))
async def news_from_panel(query: CallbackQuery) -> None:
    await edit_view(query, render_news_summary(get_important_articles()), section_keyboard("news"))
    await query.answer()


@router.callback_query(PanelAction.filter(F.section == "status"))
async def status_from_panel(query: CallbackQuery) -> None:
    await edit_view(query, render_monitoring_status(get_monitoring_status()), section_keyboard("status"))
    await query.answer()


@router.callback_query(PanelAction.filter(F.section == "activity"))
async def activity_from_panel(query: CallbackQuery) -> None:
    await edit_view(query, render_activity_list(get_recent_activity()), section_keyboard("activity"))
    await query.answer()


@router.callback_query(PanelAction.filter(F.section == "monitor"))
async def monitor_from_panel(query: CallbackQuery) -> None:
    await edit_view(query, render_monitor_overview(get_monitor_overview()), monitor_keyboard())
    await query.answer()
