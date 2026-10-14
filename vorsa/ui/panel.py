"""Tampilan teks Panel Utama (HTML Telegram)."""

from dataclasses import dataclass
from datetime import datetime
from html import escape

DIVIDER = "━━━━━━━━━━━━━━━━━━"


@dataclass(frozen=True)
class PanelSnapshot:
    bot_active: bool
    last_checked_at: datetime | None
    active_categories: int
    total_categories: int
    important_today: int
    pending_review: int
    last_activity: str | None
    generated_at: datetime


def _fmt_time(value: datetime | None) -> str:
    return value.strftime("%H:%M") if value else "belum pernah"


def render_main_panel(snap: PanelSnapshot, user_name: str | None = None) -> str:
    greeting = f"Halo, {escape(user_name)}!" if user_name else "Halo!"
    status = "🟢 Aktif" if snap.bot_active else "🔴 Berhenti"
    activity = escape(snap.last_activity) if snap.last_activity else "Belum ada aktivitas."

    return "\n".join(
        [
            "<b>VORSA · Panel Utama</b>",
            greeting,
            DIVIDER,
            "📡 <b>Status Pemantauan</b>",
            f"{status} · cek terakhir {_fmt_time(snap.last_checked_at)}",
            f"Kategori aktif: {snap.active_categories}/{snap.total_categories}",
            "",
            "📰 <b>Berita Masuk</b>",
            f"{snap.important_today} berita penting hari ini",
            f"{snap.pending_review} menunggu persetujuan",
            "",
            "🕘 <b>Aktivitas Terakhir</b>",
            activity,
            DIVIDER,
            f"<i>Diperbarui {snap.generated_at:%H:%M:%S} · pilih menu di bawah</i>",
        ]
    )
