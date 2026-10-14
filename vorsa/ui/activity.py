"""Tampilan teks daftar aktivitas terakhir (dari activity_logs)."""

from dataclasses import dataclass
from datetime import date, datetime
from html import escape

# action di activity_logs → (ikon, label)
ACTION_LABELS = {
    "design_created": ("🎨", "Desain dibuat"),
    "design_revised": ("✏️", "Desain direvisi"),
    "approved": ("✅", "Disetujui"),
    "rejected": ("❌", "Ditolak"),
    "published": ("📤", "Terkirim ke Instagram"),
    "flagged": ("📌", "Ditandai untuk diolah"),
    "category_toggled": ("🗂", "Kategori diubah"),
    "source_added": ("➕", "Sumber RSS ditambah"),
    "source_deleted": ("🗑", "Sumber RSS dihapus"),
}


@dataclass(frozen=True)
class ActivityEntry:
    action: str
    detail: str
    created_at: datetime


def describe_activity(entry: ActivityEntry) -> str:
    """Satu baris ringkas tanpa jam, dipakai juga di Panel Utama."""
    _, label = ACTION_LABELS.get(entry.action, ("•", entry.action))
    return f"{label} — {entry.detail}"


def _day_heading(day: date, today: date) -> str:
    if day == today:
        return "Hari ini"
    if (today - day).days == 1:
        return "Kemarin"
    return f"{day:%d/%m/%Y}"


def render_activity_list(entries: list[ActivityEntry], limit: int = 10, today: date | None = None) -> str:
    today = today or date.today()
    lines = ["<b>🕘 Aktivitas Terakhir</b>"]
    if not entries:
        lines += ["", "Belum ada aktivitas."]
        return "\n".join(lines)

    current_day = None
    for entry in sorted(entries, key=lambda e: e.created_at, reverse=True)[:limit]:
        day = entry.created_at.date()
        if day != current_day:
            current_day = day
            lines += ["", f"<b>{_day_heading(day, today)}</b>"]
        icon, label = ACTION_LABELS.get(entry.action, ("•", entry.action))
        lines.append(f"{entry.created_at:%H:%M} {icon} {escape(label)} — {escape(entry.detail)}")
    return "\n".join(lines)
