"""Handler kartu notifikasi berita penting."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from vorsa.handlers.common import edit_view
from vorsa.handlers.design_progress import DesignProgress, run_demo_steps
from vorsa.keyboards.news import ArticleAction, flag_confirm_keyboard, notification_keyboard, score_keyboard
from vorsa.keyboards.design import (
    REGEN_STYLES,
    DesignAction,
    RegenAction,
    design_keyboard,
    history_keyboard,
    preview_keyboard,
    regenerate_keyboard,
)
from vorsa.stub.samples import (
    add_sample_version,
    sample_design,
    sample_design_by_id,
    sample_design_image,
    sample_design_versions,
    sample_notification,
    sample_score_detail,
    set_sample_flag,
)
from vorsa.ui.design import (
    render_design_draft,
    render_preview_caption,
    render_regenerate_prompt,
    render_version_history,
)
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


def _is_sample(callback_data: DesignAction | RegenAction) -> bool:
    return sample_design_by_id(callback_data.id) is not None


@router.callback_query(DesignAction.filter(F.action == "preview"), lambda q, callback_data: _is_sample(callback_data))
async def preview_design(query: CallbackQuery, callback_data: DesignAction) -> None:
    design = sample_design_by_id(callback_data.id)
    await query.answer()
    await query.bot.send_photo(
        chat_id=query.message.chat.id,
        photo=BufferedInputFile(sample_design_image(design.headline), filename="vorsa-pratinjau.png"),
        caption=render_preview_caption(design),
        reply_markup=preview_keyboard(design.id),
    )


@router.callback_query(DesignAction.filter(F.action == "open"), lambda q, callback_data: _is_sample(callback_data))
async def open_design_chat(query: CallbackQuery) -> None:
    design = sample_design_versions()[0]
    await query.answer()
    await query.bot.send_message(
        chat_id=query.message.chat.id,
        text=render_design_draft(design),
        reply_markup=design_keyboard(design.id, design.article_id),
    )


@router.callback_query(DesignAction.filter(F.action == "history"), lambda q, callback_data: _is_sample(callback_data))
async def design_history(query: CallbackQuery) -> None:
    versions = sample_design_versions()
    await edit_view(query, render_version_history(versions), history_keyboard(versions, versions[0].id))
    await query.answer()


@router.callback_query(DesignAction.filter(F.action == "regenerate"), lambda q, callback_data: _is_sample(callback_data))
async def ask_regenerate(query: CallbackQuery, callback_data: DesignAction) -> None:
    latest = sample_design_versions()[0]
    await query.answer()
    await query.bot.send_message(
        chat_id=query.message.chat.id,
        text=render_regenerate_prompt(latest),
        reply_markup=regenerate_keyboard(latest.id),
    )


@router.callback_query(RegenAction.filter(F.style.in_(REGEN_STYLES)), lambda q, callback_data: _is_sample(callback_data))
async def regenerate(query: CallbackQuery, callback_data: RegenAction) -> None:
    await query.answer(f"🔁 Bikin versi baru: {REGEN_STYLES[callback_data.style]}")
    latest = sample_design_versions()[0]
    await run_demo_steps(DesignProgress(query, latest.article_title))
    design = add_sample_version(callback_data.style)
    await edit_view(query, render_design_draft(design), design_keyboard(design.id, design.article_id))
