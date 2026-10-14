"""Tampilan teks hub Pantau Berita Otomatis."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MonitorOverview:
    running: bool
    interval_minutes: int
    last_checked_at: datetime | None
    next_check_at: datetime | None
    active_categories: int
    total_categories: int
    active_sources: int
    failing_sources: int
    fetched_today: int  # berita baru yang diambil hari ini
    duplicates_skipped_today: int  # berita kembar yang dibuang hari ini
    important_today: int  # yang lolos saring


def _time(value: datetime | None) -> str:
    return f"{value:%H:%M}" if value else "—"


def render_monitor_overview(o: MonitorOverview) -> str:
    state = "🟢 Berjalan" if o.running else "⏸ Dijeda"
    sources = f"{o.active_sources} aktif"
    if o.failing_sources:
        sources += f" · ⚠️ {o.failing_sources} gagal"
    return "\n".join(
        [
            "<b>🛰 Pantau Berita Otomatis</b>",
            "",
            f"Status: {state} · tiap {o.interval_minutes} menit",
            f"Cek terakhir {_time(o.last_checked_at)} · berikutnya {_time(o.next_check_at) if o.running else '—'}",
            "",
            f"🗂 Kategori: {o.active_categories}/{o.total_categories} aktif",
            f"🔗 Sumber RSS: {sources}",
            "",
            "<b>Hari ini</b>",
            f"📥 {o.fetched_today} berita diambil",
            f"🔁 {o.duplicates_skipped_today} berita kembar dibuang",
            f"⭐ {o.important_today} lolos saring",
        ]
    )
