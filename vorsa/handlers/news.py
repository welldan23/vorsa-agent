"""Handler kartu notifikasi berita penting."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from vorsa.handlers.common import edit_view
from vorsa.handlers.design_progress import DesignProgress, run_demo_steps
from vorsa.keyboards.news import ArticleAction, flag_confirm_keyboard, notification_keyboard, score_keyboard
from vorsa.keyboards.design import design_keyboard
from vorsa.stub.samples import sample_design, sample_notification, sample_score_detail, set_sample_flag
from vorsa.ui.design import render_design_draft
from vorsa.ui.notification import render_flag_confirmation, render_notification
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


@router.callback_query(ArticleAction.filter((F.action == "flag") & (F.id == 0)))
async def flag(query: CallbackQuery) -> None:
    set_sample_flag(True)
    await edit_view(query, render_flag_confirmation(sample_notification()), flag_confirm_keyboard(0))
    await query.answer("📌 Ditandai")


@router.callback_query(ArticleAction.filter((F.action == "unflag") & (F.id == 0)))
async def unflag(query: CallbackQuery) -> None:
    set_sample_flag(False)
    n = sample_notification()
    await edit_view(query, render_notification(n), notification_keyboard(n))
    await query.answer("Tanda dibatalkan")


@router.callback_query(ArticleAction.filter((F.action == "design") & (F.id == 0)))
async def start_design(query: CallbackQuery) -> None:
    await query.answer("🎨 Mulai bikin desain…")
    design = sample_design()
    await run_demo_steps(DesignProgress(query, design.article_title))
    await edit_view(query, render_design_draft(design), design_keyboard(design.id, design.article_id))
