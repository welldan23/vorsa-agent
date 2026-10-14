"""Tampilan teks kelola sumber RSS."""

from dataclasses import dataclass
from datetime import datetime
from html import escape
from urllib.parse import urlparse

from vorsa.ui.categories import CategoryItem


@dataclass(frozen=True)
class RssSourceItem:
    id: int
    category_id: int
    url: str
    is_active: bool
    failing: bool  # gagal diambil pada cek terakhir
    last_fetched_at: datetime | None


def short_url(url: str, max_len: int = 40) -> str:
    """URL ringkas untuk tombol: host + path, dipotong kalau kepanjangan."""
    parsed = urlparse(url)
    text = (parsed.netloc + parsed.path).removeprefix("www.").rstrip("/")
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def _status(src: RssSourceItem) -> str:
    if not src.is_active:
        return "⏸ nonaktif"
    if src.failing:
        return "⚠️ gagal diambil"
    fetched = f"{src.last_fetched_at:%H:%M}" if src.last_fetched_at else "belum pernah"
    return f"✅ diambil {fetched}"


def render_source_categories(categories: list[CategoryItem]) -> str:
    total = sum(c.source_count for c in categories)
    return "\n".join(
        [
            "<b>🔗 Sumber RSS</b>",
            f"{total} sumber aktif di {len(categories)} kategori",
            "",
            "Pilih kategori untuk melihat, menambah, atau menghapus sumbernya.",
        ]
    )


def render_source_list(category: CategoryItem, sources: list[RssSourceItem]) -> str:
    lines = [f"<b>🔗 Sumber RSS · {escape(category.name)}</b>", ""]
    if not sources:
        lines.append("Belum ada sumber. Tekan ➕ untuk menambah.")
    for i, src in enumerate(sources, start=1):
        lines += [f"{i}. <code>{escape(src.url)}</code>", f"    {_status(src)}"]
    lines += ["", "<i>Tekan 🗑 untuk menghapus sumber.</i>" if sources else ""]
    return "\n".join(lines).rstrip()


def render_delete_confirm(src: RssSourceItem) -> str:
    return f"Hapus sumber ini?\n\n<code>{escape(src.url)}</code>\n\nBerita lama dari sumber ini tetap tersimpan."


def render_add_prompt(category: CategoryItem) -> str:
    return (
        f"<b>➕ Tambah sumber · {escape(category.name)}</b>\n\n"
        "Kirim URL feed RSS-nya di chat ini, contoh:\n"
        "<code>https://contoh.com/rss</code>\n\n"
        "Ketik /batal untuk membatalkan."
    )
