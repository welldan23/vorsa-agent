"""Tampilkan kemajuan pembuatan desain di chat (pesan yang diperbarui per langkah)."""

import asyncio

from aiogram.enums import ChatAction
from aiogram.types import CallbackQuery

from vorsa.handlers.common import edit_view
from vorsa.ui.design import DESIGN_STEPS, render_design_progress

# Jeda antar langkah untuk data contoh (dibuat 0 di tes).
DEMO_STEP_DELAY = 0.7


class DesignProgress:
    """Ganti isi pesan tombol dengan status langkah; dipanggil tiap langkah dimulai."""

    def __init__(self, query: CallbackQuery, article_title: str):
        self.query = query
        self.article_title = article_title

    async def step(self, index: int) -> None:
        if self.query.message is not None:
            await self.query.bot.send_chat_action(self.query.message.chat.id, ChatAction.UPLOAD_PHOTO)
        await edit_view(self.query, render_design_progress(self.article_title, index), None)


async def run_demo_steps(progress: DesignProgress) -> None:
    """Sementara: jalankan semua langkah dengan jeda singkat sampai backend desain ada."""
    for index in range(len(DESIGN_STEPS)):
        await progress.step(index)
        await asyncio.sleep(DEMO_STEP_DELAY)
