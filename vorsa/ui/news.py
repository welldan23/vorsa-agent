"""Tampilan teks ringkasan berita yang lolos saring."""

from dataclasses import dataclass
from datetime import datetime
from html import escape


@dataclass(frozen=True)
class ArticleSummary:
    title: str
    category: str
    source: str
    link: str
    relevance_score: float  # 0–1, dari AI filter
    published_at: datetime


def score_badge(score: float) -> str:
    if score >= 0.85:
        return "🔥"
    if score >= 0.7:
        return "⭐"
    return "•"


def render_news_summary(articles: list[ArticleSummary], limit: int = 5) -> str:
    lines = ["<b>📰 Berita Terbaru</b>", "<i>Hanya berita yang lolos saring</i>", ""]
    if not articles:
        lines.append("Belum ada berita penting. Nanti VORSA kabari kalau ada yang masuk 👀")
        return "\n".join(lines)

    shown = sorted(articles, key=lambda a: a.published_at, reverse=True)[:limit]
    for i, a in enumerate(shown, start=1):
        lines += [
            f"{i}. {score_badge(a.relevance_score)} <a href=\"{escape(a.link)}\">{escape(a.title)}</a>",
            f"    {escape(a.category)} · {escape(a.source)} · {a.published_at:%H:%M}"
            f" · skor {a.relevance_score:.0%}",
            "",
        ]
    if len(articles) > limit:
        lines.append(f"<i>+{len(articles) - limit} berita lainnya</i>")
    lines.append("🔥 sangat penting · ⭐ penting")
    return "\n".join(lines)
