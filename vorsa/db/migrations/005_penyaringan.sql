-- Penyaringan AI & notifikasi berita penting.

-- Hasil penilaian AI per berita (relevance_score & is_important sudah ada sejak 001).
ALTER TABLE articles ADD COLUMN relevance_reason   TEXT;  -- alasan singkat kenapa penting
ALTER TABLE articles ADD COLUMN relevance_criteria TEXT;  -- JSON {"impact": 0.9, ...}
ALTER TABLE articles ADD COLUMN scored_at          TEXT;  -- NULL = belum dinilai AI
ALTER TABLE articles ADD COLUMN notified_at        TEXT;  -- NULL = belum dikirim sebagai notifikasi
ALTER TABLE articles ADD COLUMN is_ignored         INTEGER NOT NULL DEFAULT 0 CHECK (is_ignored IN (0, 1));

-- Antrean berita yang belum dinilai, terlama dulu.
CREATE INDEX idx_articles_unscored ON articles (fetched_at) WHERE scored_at IS NULL;
-- Antrean berita penting yang belum dikirim.
CREATE INDEX idx_articles_unnotified ON articles (fetched_at) WHERE is_important = 1 AND notified_at IS NULL;

-- Pesan notifikasi yang terkirim, supaya kartunya bisa diperbarui (mis. setelah ditandai).
CREATE TABLE notifications (
    id         INTEGER PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chat_id    INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    sent_at    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (article_id, user_id)
);

CREATE INDEX idx_notifications_article ON notifications (article_id);
