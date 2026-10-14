"""Handler kartu notifikasi berita penting."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from vorsa.keyboards.news import notification_keyboard
from vorsa.stub.samples import sample_notification
from vorsa.ui.notification import render_notification

router = Router(name="news")


@router.message(Command("contoh_notif"))
async def demo_notification(message: Message) -> None:
    """Sementara: kirim contoh notifikasi sampai pengiriman otomatis dibuat."""
    n = sample_notification()
    await message.answer(render_notification(n), reply_markup=notification_keyboard(n))
