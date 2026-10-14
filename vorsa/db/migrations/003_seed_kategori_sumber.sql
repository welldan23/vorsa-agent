-- Isi awal: 7 kategori dari PRD + sumber RSS bawaan (sudah dicek bisa diakses, Okt 2026).
-- Hanya dijalankan sekali; sumber yang nanti dihapus pemilik tidak akan muncul lagi.

INSERT OR IGNORE INTO categories (name, min_relevance) VALUES
    ('Teknologi & AI', 0.70),
    ('Ekonomi & Bisnis', 0.70),
    ('Berita Nasional', 0.75),
    ('Culture & Entertainment', 0.65),
    ('Berita Internasional', 0.75),
    ('Musik & Lifestyle', 0.60),
    ('Tren Internet', 0.60);

INSERT OR IGNORE INTO rss_sources (category_id, url)
SELECT c.id, s.url
FROM (
    SELECT 'Teknologi & AI' AS category, 'https://www.theverge.com/rss/index.xml' AS url
    UNION ALL SELECT 'Teknologi & AI', 'https://techcrunch.com/feed/'
    UNION ALL SELECT 'Teknologi & AI', 'https://www.antaranews.com/rss/tekno.xml'
    UNION ALL SELECT 'Ekonomi & Bisnis', 'https://www.cnbcindonesia.com/market/rss'
    UNION ALL SELECT 'Ekonomi & Bisnis', 'https://www.antaranews.com/rss/ekonomi.xml'
    UNION ALL SELECT 'Berita Nasional', 'https://www.cnbcindonesia.com/news/rss'
    UNION ALL SELECT 'Berita Nasional', 'https://www.antaranews.com/rss/terkini.xml'
    UNION ALL SELECT 'Berita Nasional', 'https://rss.tempo.co/nasional'
    UNION ALL SELECT 'Culture & Entertainment', 'https://www.antaranews.com/rss/hiburan.xml'
    UNION ALL SELECT 'Berita Internasional', 'https://feeds.bbci.co.uk/news/world/rss.xml'
    UNION ALL SELECT 'Berita Internasional', 'https://www.aljazeera.com/xml/rss/all.xml'
    UNION ALL SELECT 'Berita Internasional', 'https://www.antaranews.com/rss/dunia.xml'
    UNION ALL SELECT 'Musik & Lifestyle', 'https://www.rollingstone.com/music/feed/'
    UNION ALL SELECT 'Musik & Lifestyle', 'https://www.antaranews.com/rss/lifestyle.xml'
    UNION ALL SELECT 'Tren Internet', 'https://trends.google.com/trending/rss?geo=ID'
) AS s
JOIN categories c ON c.name = s.category;
