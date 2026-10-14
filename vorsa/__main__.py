"""Titik masuk: `python -m vorsa` (bot) atau `python -m vorsa --preview` (cetak panel di terminal)."""

import asyncio
import logging
import re
import sys

from vorsa.config import load_settings


def preview() -> None:
    from vorsa.keyboards.panel import main_panel_keyboard
    from vorsa.stub.mock_data import get_panel_snapshot
    from vorsa.ui.panel import render_main_panel

    text = render_main_panel(get_panel_snapshot(), "Pemilik")
    print(re.sub(r"</?[bi]>", "", text))
    print()
    for row in main_panel_keyboard().inline_keyboard:
        print("  ".join(f"[ {btn.text} ]" for btn in row))


async def run_bot(token: str) -> None:
    from vorsa.bot import create_bot, create_dispatcher, register_commands

    bot = create_bot(token)
    dp = create_dispatcher()
    await register_commands(bot)
    await dp.start_polling(bot)


def main() -> None:
    if "--preview" in sys.argv:
        preview()
        return

    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    if not settings.bot_token:
        sys.exit("BOT_TOKEN belum diisi. Salin .env.example jadi .env lalu isi token dari @BotFather.")
    asyncio.run(run_bot(settings.bot_token))


if __name__ == "__main__":
    main()
