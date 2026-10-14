-- Pesan error pengambilan terakhir per sumber; NULL = berhasil.
-- Dipakai Status Pemantauan untuk menghitung sumber yang gagal.
ALTER TABLE rss_sources ADD COLUMN last_error TEXT;
