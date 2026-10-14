"""Tampilan teks status pemantauan RSS."""

from dataclasses import dataclass
from datetime import datetime
from html import escape


@dataclass(frozen=True)
class CategoryStatus:
    name: str
    enabled: bool
    active_sources: int
    failing_sources: int  # sumber yang gagal diambil pada cek terakhir
    new_articles: int  # berita baru pada cek terakhir


@dataclass(frozen=True)
class MonitoringStatus:
    bot_active: bool
    interval_minutes: int
    last_checked_at: datetime | None
    next_check_at: datetime | None
    categories: list[CategoryStatus]


def _relative(value: datetime | None, now: datetime) -> str:
    if value is None:
        return "belum pernah"
    minutes = round(abs((now - value).total_seconds()) / 60)
    when = "baru saja" if minutes == 0 else (
        f"{minutes} menit lalu" if value <= now else f"{minutes} menit lagi"
    )
    return f"{value:%H:%M} ({when})"


def _category_line(cat: CategoryStatus) -> str:
    name = escape(cat.name)
    if not cat.enabled:
        return f"⏸ {name} — nonaktif"
    icon = "⚠️" if cat.failing_sources else "✅"
    line = f"{icon} {name} — {cat.active_sources} sumber · {cat.new_articles} baru"
    if cat.failing_sources:
        line += f" · {cat.failing_sources} gagal"
    return line


def render_monitoring_status(status: MonitoringStatus, now: datetime | None = None) -> str:
    now = now or datetime.now()
    enabled = [c for c in status.categories if c.enabled]
    failing = sum(c.failing_sources for c in enabled)
    state = "🟢 Aktif" if status.bot_active else "🔴 Berhenti"

    lines = [
        "<b>📡 Status Pemantauan</b>",
        "",
        f"Bot: {state}",
        f"Interval: tiap {status.interval_minutes} menit",
        f"Cek terakhir: {_relative(status.last_checked_at, now)}",
        f"Cek berikutnya: {_relative(status.next_check_at, now) if status.bot_active else '—'}",
        "",
        f"<b>Kategori</b> ({len(enabled)}/{len(status.categories)} aktif)",
    ]
    lines += [_category_line(c) for c in status.categories]
    if failing:
        lines += ["", f"<i>⚠️ {failing} sumber gagal diambil — pemantauan tetap jalan.</i>"]
    return "\n".join(lines)
