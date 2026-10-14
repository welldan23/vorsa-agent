-- Skema Panel Utama: berita, status pengecekan, aktivitas.
-- Semua waktu disimpan sebagai teks ISO-8601 UTC ("YYYY-MM-DD HH:MM:SS").
-- Tabel induk (users, categories, rss_sources) ikut dibuat di sini karena SQLite
-- menolak insert ke tabel yang FK-nya menunjuk tabel yang belum ada.

-- Pemilik/pengguna yang diizinkan memakai bot.
CREATE TABLE users (
    id          INTEGER PRIMARY KEY,
    telegram_id TEXT    NOT NULL UNIQUE,
    name        TEXT,
    role        TEXT    NOT NULL DEFAULT 'owner' CHECK (role IN ('owner', 'admin')),
    is_active   INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Kategori berita yang dipantau.
CREATE TABLE categories (
    id            INTEGER PRIMARY KEY,
    name          TEXT    NOT NULL UNIQUE,
    is_enabled    INTEGER NOT NULL DEFAULT 1 CHECK (is_enabled IN (0, 1)),
    min_relevance REAL    NOT NULL DEFAULT 0.7 CHECK (min_relevance BETWEEN 0 AND 1)
);

-- Sumber RSS per kategori.
CREATE TABLE rss_sources (
    id              INTEGER PRIMARY KEY,
    category_id     INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    url             TEXT    NOT NULL UNIQUE,
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    last_fetched_at TEXT
);

CREATE INDEX idx_rss_sources_category ON rss_sources (category_id);

-- Berita yang sudah diambil dari RSS.
CREATE TABLE articles (
    id              INTEGER PRIMARY KEY,
    source_id       INTEGER NOT NULL REFERENCES rss_sources(id) ON DELETE CASCADE,
    category_id     INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    title           TEXT    NOT NULL,
    link            TEXT    NOT NULL UNIQUE,
    summary         TEXT,
    content_hash    TEXT    NOT NULL UNIQUE,           -- buang berita kembar
    published_at    TEXT,
    relevance_score REAL    CHECK (relevance_score BETWEEN 0 AND 1),  -- NULL = belum dinilai AI
    is_important    INTEGER NOT NULL DEFAULT 0 CHECK (is_important IN (0, 1)),
    is_flagged      INTEGER NOT NULL DEFAULT 0 CHECK (is_flagged IN (0, 1)),
    fetched_at      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Ringkasan "Berita Terbaru": berita penting, terbaru dulu.
CREATE INDEX idx_articles_important ON articles (is_important, published_at DESC);
CREATE INDEX idx_articles_category ON articles (category_id, fetched_at DESC);
CREATE INDEX idx_articles_source ON articles (source_id);

-- Satu baris per putaran pengecekan RSS (dasar "Status Pemantauan" & "Cek Terakhir").
CREATE TABLE check_runs (
    id                 INTEGER PRIMARY KEY,
    started_at         TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at        TEXT,                              -- NULL = masih berjalan
    status             TEXT    NOT NULL DEFAULT 'running'
                       CHECK (status IN ('running', 'success', 'partial', 'failed')),
    sources_checked    INTEGER NOT NULL DEFAULT 0,
    sources_failed     INTEGER NOT NULL DEFAULT 0,
    new_articles       INTEGER NOT NULL DEFAULT 0,
    duplicates_skipped INTEGER NOT NULL DEFAULT 0,
    passed_filter      INTEGER NOT NULL DEFAULT 0,
    error_message      TEXT
);

CREATE INDEX idx_check_runs_started ON check_runs (started_at DESC);

-- Catatan aktivitas bot (audit trail).
CREATE TABLE activity_logs (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,  -- NULL = aksi sistem
    action     TEXT    NOT NULL,   -- design_created, approved, published, ...
    detail     TEXT,
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_logs_created ON activity_logs (created_at DESC);
