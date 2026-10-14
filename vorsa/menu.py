"""Daftar menu perintah — satu sumber untuk tombol inline, /bantuan, dan menu "/" Telegram."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MenuItem:
    section: str  # dipakai di callback_data tombol
    label: str  # teks tombol
    command: str  # perintah slash, tanpa "/"
    description: str  # muncul di menu "/" Telegram dan /bantuan
    in_panel: bool = True  # tampil sebagai tombol di Panel Utama


MENU_ITEMS: list[MenuItem] = [
    MenuItem("news", "📰 Berita Terbaru", "berita", "Ringkasan berita penting yang masuk"),
    MenuItem("status", "📡 Status", "status", "Status pemantauan & cek terakhir"),
    MenuItem("activity", "🕘 Aktivitas", "aktivitas", "Riwayat aksi terakhir"),
    MenuItem("monitor", "🛰 Pantau Berita", "pantau", "Panel pemantauan RSS otomatis"),
    MenuItem("categories", "🗂 Kategori", "kategori", "Aktif/nonaktifkan kategori berita", in_panel=False),
    MenuItem("sources", "🔗 Sumber RSS", "sumber", "Tambah atau hapus sumber RSS", in_panel=False),
    MenuItem("filter", "🎚 Penyaringan", "saring", "Atur seberapa ketat berita disaring"),
    MenuItem("settings", "⚙️ Pengaturan", "pengaturan", "Pengaturan bot"),
    MenuItem("help", "❓ Bantuan", "bantuan", "Daftar perintah VORSA"),
]

PANEL_COMMAND = ("panel", "Buka Panel Utama")

MENU_BY_COMMAND = {item.command: item for item in MENU_ITEMS}
