-- Migration: Criação da tabela progress_post

CREATE TABLE IF NOT EXISTS progress_post (
    id SERIAL PRIMARY KEY,
    id_post INTEGER NOT NULL REFERENCES posts(id_post) ON DELETE CASCADE,
    id_user INTEGER NOT NULL REFERENCES users(id_user) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL DEFAULT 'in_progress'
        CHECK (status IN ('not_started', 'in_progress', 'completed')),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT uq_progress_post_user UNIQUE (id_user, id_post)
);

CREATE INDEX IF NOT EXISTS idx_progress_post_id_user ON progress_post (id_user);
CREATE INDEX IF NOT EXISTS idx_progress_post_id_post ON progress_post (id_post);
