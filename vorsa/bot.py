"""Perakitan Bot + Dispatcher aiogram."""

import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from vorsa.config import Settings
from vorsa.handlers import build_router
from vorsa.menu import MENU_ITEMS, PANEL_COMMAND


def create_bot(token: str) -> Bot:
    return Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


def create_dispatcher(db: sqlite3.Connection, settings: Settings) -> Dispatcher:
    """`db` dan `settings` bisa diminta handler sebagai parameter bernama sama."""
    dp = Dispatcher(db=db, settings=settings)
    dp.include_router(build_router())
    return dp


async def register_commands(bot: Bot) -> None:
    """Isi menu "/" di Telegram supaya perintah bisa dipilih tanpa diketik."""
    commands = [BotCommand(command=PANEL_COMMAND[0], description=PANEL_COMMAND[1])]
    commands += [BotCommand(command=i.command, description=i.description) for i in MENU_ITEMS]
    await bot.set_my_commands(commands)
