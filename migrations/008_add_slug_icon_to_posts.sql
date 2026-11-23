-- Migration: campos que o app usa nos posts e que faltavam na tabela
--   slug: identificador do post na URL (/post/<slug>), único
--   icon: ícone escolhido no cadastro do post (classe do Bootstrap Icons)
-- Pode ser rodada mais de uma vez sem problema.

ALTER TABLE posts ADD COLUMN IF NOT EXISTS slug VARCHAR(255);
ALTER TABLE posts ADD COLUMN IF NOT EXISTS icon VARCHAR(50) NOT NULL DEFAULT 'bi-code-slash';

-- posts criados antes desta migration recebem um slug provisório
UPDATE posts SET slug = 'post-' || id_post::text WHERE slug IS NULL;

ALTER TABLE posts ALTER COLUMN slug SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_posts_slug ON posts (slug);
