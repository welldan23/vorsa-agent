"""Tampilan menu tingkat penyaringan."""

from html import escape

from vorsa.ui.categories import CategoryItem
from vorsa.ui.score import score_bar


def render_filter_menu(categories: list[CategoryItem], preset: str | None) -> str:
    mode = f"<b>{preset.capitalize()}</b>" if preset else "<b>Campuran</b> (beda per kategori)"
    lines = [
        "<b>🎚 Tingkat Penyaringan</b>",
        "Berita baru dikirim kalau skor AI-nya ≥ ambang kategori.",
        "Makin tinggi ambang → makin sedikit tapi makin penting.",
        "",
        f"Mode: {mode}",
        "",
    ]
    for c in categories:
        off = " <i>(nonaktif)</i>" if not c.enabled else ""
        lines.append(f"<code>{score_bar(c.min_relevance)}</code> {c.min_relevance:.0%} {escape(c.name)}{off}")
    lines += ["", "<i>Pilih preset, atau pakai ➖/➕ per kategori (5%).</i>"]
    return "\n".join(lines)
