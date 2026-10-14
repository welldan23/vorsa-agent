"""Helper bersama untuk handler."""

import logging
from enum import Enum

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, LinkPreviewOptions, Message

PLACEHOLDER = "Bagian ini sedang disiapkan 🙏"
NO_PREVIEW = LinkPreviewOptions(is_disabled=True)

log = logging.getLogger(__name__)


class EditResult(Enum):
    EDITED = "edited"  # pesan lama diganti isinya
    UNCHANGED = "unchanged"  # isi sama persis, tidak ada yang perlu diganti
    RESENT = "resent"  # pesan lama tidak bisa diedit, dikirim pesan baru


async def edit_view(query: CallbackQuery, text: str, reply_markup) -> EditResult:
    """Ganti isi pesan tempat tombol ditekan dengan tampilan baru.

    Kalau pesannya sudah tidak bisa diedit (terhapus, atau lebih dari 48 jam),
    tampilan dikirim sebagai pesan baru supaya pengguna tetap dapat data terbaru.
    """
    if isinstance(query.message, Message):
        try:
            await query.message.edit_text(text, reply_markup=reply_markup, link_preview_options=NO_PREVIEW)
            return EditResult.EDITED
        except TelegramBadRequest as err:
            if "message is not modified" in err.message:
                return EditResult.UNCHANGED
            log.info("Pesan tidak bisa diedit (%s), kirim pesan baru", err.message)

    await query.bot.send_message(
        chat_id=query.from_user.id if query.message is None else query.message.chat.id,
        text=text,
        reply_markup=reply_markup,
        link_preview_options=NO_PREVIEW,
    )
    return EditResult.RESENT
