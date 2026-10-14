"""Helper bersama untuk handler."""

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, LinkPreviewOptions

PLACEHOLDER = "Bagian ini sedang disiapkan 🙏"
NO_PREVIEW = LinkPreviewOptions(is_disabled=True)


async def edit_view(query: CallbackQuery, text: str, reply_markup) -> None:
    """Ganti isi pesan panel dengan tampilan baru."""
    try:
        await query.message.edit_text(text, reply_markup=reply_markup, link_preview_options=NO_PREVIEW)
    except TelegramBadRequest:
        # Isi pesan tidak berubah — Telegram menolak edit yang sama persis.
        pass
