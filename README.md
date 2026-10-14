# VORSA

Asisten berita Telegram-first: pantau RSS → saring pakai AI → desain VORSA → setujui → kirim ke Instagram.
Semua dikendalikan lewat chat Telegram (tanpa dashboard web).

## Jalankan

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env        # isi BOT_TOKEN dari @BotFather & OWNER_TELEGRAM_IDS
.venv/bin/python -m vorsa
```

Lalu kirim `/start` ke bot kamu di Telegram.

Bot ini privat: hanya ID Telegram di `OWNER_TELEGRAM_IDS` yang dilayani. Belum tahu ID-mu?
Kirim `/start` dulu — bot akan menolak sambil memberi tahu ID-mu. Masukkan ke `.env`, lalu
nyalakan ulang bot. Database SQLite (`data/vorsa.sqlite3`) dibuat
dan diperbarui otomatis saat bot menyala; bisa juga manual dengan `.venv/bin/python -m vorsa --migrate`.

## Tes

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest
```

Mau lihat Panel Utama (dari database) tanpa token? Jalankan:

```bash
.venv/bin/python -m vorsa --preview
```

Begitu menyala, bot langsung mengecek semua sumber RSS lalu mengulanginya tiap
`CHECK_INTERVAL_MINUTES` menit (bawaan 15). Berita disimpan di SQLite, berita kembar dibuang.

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
| `vorsa/services/` | Logika & akses data (berita, pemantauan, fetcher RSS, dedup, dll.) |
| `vorsa/middlewares/` | Satpam akses: hanya pemilik terdaftar |
| `vorsa/scheduler.py` | Jadwal cek RSS otomatis (APScheduler) |
| `vorsa/db/` | Koneksi SQLite & migrasi skema (`migrations/NNN_nama.sql`) |
