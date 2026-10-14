"""Handler kartu notifikasi berita penting."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from vorsa.handlers.common import edit_view
from vorsa.keyboards.news import ArticleAction, notification_keyboard, score_keyboard
from vorsa.stub.samples import sample_notification, sample_score_detail
from vorsa.ui.notification import render_notification
from vorsa.ui.score import render_score_detail

router = Router(name="news")


@router.message(Command("contoh_notif"))
async def demo_notification(message: Message) -> None:
    """Sementara: kirim contoh notifikasi sampai pengiriman otomatis dibuat."""
    n = sample_notification()
    await message.answer(render_notification(n), reply_markup=notification_keyboard(n))


# Sementara hanya berita contoh (id 0); berita asli menyusul di backend.
@router.callback_query(ArticleAction.filter((F.action == "score") & (F.id == 0)))
async def show_score(query: CallbackQuery) -> None:
    await edit_view(query, render_score_detail(sample_score_detail()), score_keyboard(0))
    await query.answer()


@router.callback_query(ArticleAction.filter((F.action == "card") & (F.id == 0)))
async def back_to_card(query: CallbackQuery) -> None:
    n = sample_notification()
    await edit_view(query, render_notification(n), notification_keyboard(n))
    await query.answer()
