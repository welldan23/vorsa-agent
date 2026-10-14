"""Tampilan teks daftar kategori berita."""

from dataclasses import dataclass
from html import escape


@dataclass(frozen=True)
class CategoryItem:
    id: int
    name: str
    enabled: bool
    min_relevance: float  # ambang relevansi khusus kategori (0–1)
    source_count: int


def render_category_list(items: list[CategoryItem]) -> str:
    active = sum(c.enabled for c in items)
    lines = [
        "<b>🗂 Kategori Berita</b>",
        f"{active}/{len(items)} kategori dipantau",
        "",
    ]
    for c in items:
        icon = "✅" if c.enabled else "⏸"
        lines.append(
            f"{icon} {escape(c.name)} — {c.source_count} sumber · ambang {c.min_relevance:.0%}"
        )
    lines.append("")
    if active == 0:
        lines.append("⚠️ <i>Semua kategori nonaktif — tidak ada berita yang dipantau.</i>")
    else:
        lines.append("<i>Tekan nama kategori untuk menyalakan/mematikan.</i>")
    return "\n".join(lines)
