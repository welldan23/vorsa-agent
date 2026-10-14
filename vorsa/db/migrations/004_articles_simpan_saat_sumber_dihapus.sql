-- Berita tetap tersimpan saat sumbernya dihapus (source_id jadi NULL), karena nanti
-- desain, persetujuan, dan publikasi menempel ke berita. SQLite tidak bisa mengubah
-- FK lewat ALTER, jadi tabel dibangun ulang.

CREATE TABLE articles_baru (
    id              INTEGER PRIMARY KEY,
    source_id       INTEGER REFERENCES rss_sources(id) ON DELETE SET NULL,  -- NULL = sumber dihapus
    category_id     INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    title           TEXT    NOT NULL,
    link            TEXT    NOT NULL UNIQUE,
    summary         TEXT,
    content_hash    TEXT    NOT NULL UNIQUE,
    published_at    TEXT,
    relevance_score REAL    CHECK (relevance_score BETWEEN 0 AND 1),
    is_important    INTEGER NOT NULL DEFAULT 0 CHECK (is_important IN (0, 1)),
    is_flagged      INTEGER NOT NULL DEFAULT 0 CHECK (is_flagged IN (0, 1)),
    fetched_at      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO articles_baru SELECT * FROM articles;
DROP TABLE articles;
ALTER TABLE articles_baru RENAME TO articles;

CREATE INDEX idx_articles_important ON articles (is_important, published_at DESC);
CREATE INDEX idx_articles_category ON articles (category_id, fetched_at DESC);
CREATE INDEX idx_articles_source ON articles (source_id);
