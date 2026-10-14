"""Tampilan chat desain VORSA."""

from dataclasses import dataclass
from datetime import datetime
from html import escape

STATUS_LABELS = {
    "draft": "📝 Draf",
    "review": "👀 Menunggu persetujuan",
    "approved": "✅ Disetujui",
    "published": "📤 Sudah tayang",
}


@dataclass(frozen=True)
class DesignDraft:
    id: int
    article_id: int
    article_title: str
    category: str
    version: int
    status: str  # draft | review | approved | published (designs.status)
    headline: str  # teks besar di gambar
    caption: str  # caption Instagram
    hashtags: list[str]
    created_at: datetime


def render_design_progress(article_title: str) -> str:
    return (
        "🎨 <b>Lagi bikin desain VORSA…</b>\n\n"
        f"<i>{escape(article_title)}</i>\n\n"
        "Menyusun judul, caption, dan tata letak. Biasanya kurang dari satu menit."
    )


def render_design_draft(d: DesignDraft) -> str:
    tags = " ".join(f"#{escape(t)}" for t in d.hashtags)
    lines = [
        f"🎨 <b>Desain VORSA</b> · versi {d.version} · {STATUS_LABELS.get(d.status, escape(d.status))}",
        f"<i>Dari berita: {escape(d.article_title)}</i>",
        f"<i>{escape(d.category)} · dibuat {d.created_at:%H:%M}</i>",
        "",
        "<b>Judul di gambar</b>",
        f"“{escape(d.headline)}”",
        "",
        "<b>Caption Instagram</b>",
        escape(d.caption),
    ]
    if tags:
        lines += ["", tags]
    return "\n".join(lines)
