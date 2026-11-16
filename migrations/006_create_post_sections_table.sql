-- Migration: Create post_sections table (N -> 1 relationship with posts)

CREATE TABLE IF NOT EXISTS post_sections (
    id_post_section SERIAL PRIMARY KEY,
    id_post INTEGER NOT NULL REFERENCES posts(id_post) ON DELETE CASCADE,
    subtitle VARCHAR(255),
    text TEXT NOT NULL,
    url_img VARCHAR(500),
    display_order INTEGER NOT NULL DEFAULT 1,
    status BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_post_sections_id_post ON post_sections (id_post);
