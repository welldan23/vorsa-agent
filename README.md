# VORSA

Asisten berita Telegram-first: pantau RSS → saring pakai AI → desain VORSA → setujui → kirim ke Instagram.
Semua dikendalikan lewat chat Telegram (tanpa dashboard web).

## Jalankan

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env        # isi BOT_TOKEN dari @BotFather
.venv/bin/python -m vorsa
```

Lalu kirim `/start` ke bot kamu di Telegram.

Mau lihat tampilan Panel Utama tanpa token? Jalankan:

```bash
.venv/bin/python -m vorsa --preview
```

> Saat ini semua tampilan masih memakai data tiruan di memori (`vorsa/stub/mock_data.py`).
> Perubahan (toggle kategori, tambah/hapus sumber RSS) hilang saat bot di-restart.

## Perintah

| Perintah | Fungsi |
|---|---|
| `/start`, `/panel` | Panel Utama |
| `/berita` | Ringkasan berita yang lolos saring |
| `/status` | Status pemantauan & waktu cek |
| `/aktivitas` | Riwayat aksi terakhir |
| `/pantau` | Hub Pantau Berita (cek terakhir, kategori, sumber RSS) |
| `/kategori` | Nyalakan/matikan kategori |
| `/sumber` | Tambah/hapus sumber RSS |
| `/bantuan` | Daftar perintah |

## Struktur

| Folder | Isi |
|---|---|
| `vorsa/menu.py` | Daftar menu perintah (tombol, `/bantuan`, menu "/" Telegram) |
| `vorsa/handlers/` | Handler perintah & tombol (aiogram Router; `fallback.py` selalu terakhir) |
| `vorsa/keyboards/` | Tombol inline |
| `vorsa/ui/` | Teks/tampilan pesan |
| `vorsa/stub/` | Data tiruan sebelum backend jadi |
