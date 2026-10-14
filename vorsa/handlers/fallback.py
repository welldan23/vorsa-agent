"""Penangkap terakhir: menu yang belum punya tampilan. Router ini harus didaftarkan paling akhir."""

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message

from vorsa.handlers.common import PLACEHOLDER
from vorsa.keyboards.monitor import MonitorAction
from vorsa.keyboards.news import ArticleAction
from vorsa.keyboards.panel import PanelAction, back_to_panel_keyboard
from vorsa.menu import MENU_BY_COMMAND

router = Router(name="fallback")


@router.message(Command(*MENU_BY_COMMAND))
async def command_placeholder(message: Message, command: CommandObject) -> None:
    item = MENU_BY_COMMAND[command.command]
    await message.answer(f"<b>{item.label}</b>\n{PLACEHOLDER}", reply_markup=back_to_panel_keyboard())


@router.callback_query(PanelAction.filter())
@router.callback_query(MonitorAction.filter())
@router.callback_query(ArticleAction.filter())
async def section_placeholder(query: CallbackQuery) -> None:
    await query.answer(PLACEHOLDER, show_alert=True)
