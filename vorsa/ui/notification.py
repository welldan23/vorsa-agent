"""Tampilan kartu notifikasi berita penting."""

from dataclasses import dataclass
from datetime import datetime
from html import escape

from vorsa.ui.news import score_badge

SUMMARY_MAX_CHARS = 300


@dataclass(frozen=True)
class ArticleNotification:
    id: int
    title: str
    category: str
    source: str
    link: str
    summary: str
    relevance_score: float
    reason: str | None  # alasan singkat dari AI kenapa berita ini penting
    published_at: datetime | None
    is_flagged: bool = False


def _short(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def render_notification(n: ArticleNotification) -> str:
    when = f" · {n.published_at:%H:%M}" if n.published_at else ""
    lines = [
        f"🔔 <b>Berita Penting</b> · {score_badge(n.relevance_score)} {n.relevance_score:.0%}",
        "",
        f"<b>{escape(n.title)}</b>",
        f"<i>{escape(n.category)} · {escape(n.source)}{when}</i>",
    ]
    if n.summary:
        lines += ["", escape(_short(n.summary, SUMMARY_MAX_CHARS))]
    if n.reason:
        lines += ["", f"💡 <i>Kenapa penting: {escape(n.reason)}</i>"]
    if n.is_flagged:
        lines += ["", "📌 <b>Sudah ditandai untuk diolah</b>"]
    return "\n".join(lines)


def render_flag_confirmation(n: ArticleNotification) -> str:
    return "\n".join(
        [
            "📌 <b>Berita ditandai untuk diolah</b>",
            "",
            f"<b>{escape(n.title)}</b>",
            f"<i>{escape(n.category)} · {escape(n.source)}</i>",
            "",
            "Mau langsung dibuatkan desain VORSA sekarang?",
            "<i>Kalau nanti, berita ini tetap tersimpan di daftar yang ditandai.</i>",
        ]
    )
