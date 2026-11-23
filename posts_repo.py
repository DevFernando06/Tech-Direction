"""
Acesso ao banco (PostgreSQL) para posts e suas seções: usado pelo cadastro,
edição, listagem, leitura e exclusão de posts.

- Só fica ativo se DATABASE_URL estiver definida no .env (mesma regra do usuarios_repo).
- Sem DATABASE_URL, o app.py continua usando o dicionário POSTS em memória.
- Os dicionários devolvidos têm o MESMO formato do POSTS em memória
  (id_post, id_user, title, description, icon, status, sections), então o
  restante do app não precisa saber de onde o post veio. Vem também
  "autor_nome", com o nome de quem escreveu o post.

Tabelas: posts e post_sections (migrations 005, 006 e 008).
"""
import usuarios_repo

_SELECT_POSTS = """
    SELECT p.id_post, p.id_user, p.slug, p.title, p.description, p.icon, p.status,
           u.name AS autor_nome
    FROM posts p
    JOIN users u ON u.id_user = p.id_user
"""

_SELECT_SECOES = """
    SELECT s.id_post, s.subtitle, s.text, s.url_img, s.display_order, s.status
    FROM post_sections s
    JOIN posts p ON p.id_post = s.id_post
"""


def _carregar(conn, filtro="", params=None):
    """Lê posts (e as seções deles) no formato do app: {slug: post}."""
    linhas = conn.execute(_SELECT_POSTS + filtro + " ORDER BY p.id_post", params).fetchall()
    posts = {}
    por_id = {}
    for linha in linhas:
        post = {
            "id_post": linha["id_post"],
            "id_user": linha["id_user"],
            "title": linha["title"],
            "description": linha["description"],
            "icon": linha["icon"],
            "status": linha["status"],
            "autor_nome": linha["autor_nome"],
            "sections": [],
        }
        posts[linha["slug"]] = post
        por_id[linha["id_post"]] = post

    if por_id:
        secoes = conn.execute(
            _SELECT_SECOES + filtro + " ORDER BY s.id_post, s.display_order", params
        ).fetchall()
        for secao in secoes:
            por_id[secao["id_post"]]["sections"].append(
                {
                    "subtitle": secao["subtitle"],
                    "text": secao["text"],
                    "url_img": secao["url_img"],
                    "display_order": secao["display_order"],
                    "status": secao["status"],
                }
            )
    return posts


def _gravar_secoes(conn, id_post, sections):
    for secao in sections:
        conn.execute(
            """
            INSERT INTO post_sections (id_post, subtitle, text, url_img, display_order, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                id_post,
                secao["subtitle"],
                secao["text"],
                secao["url_img"],
                secao["display_order"],
                secao["status"],
            ),
        )


def listar():
    """Todos os posts, do mais antigo ao mais novo: {slug: post}."""
    with usuarios_repo.conectar() as conn:
        return _carregar(conn)


def buscar(slug):
    """Um post pelo slug, ou None se não existir."""
    with usuarios_repo.conectar() as conn:
        return _carregar(conn, " WHERE p.slug = %s", (slug,)).get(slug)


def slug_existe(slug):
    with usuarios_repo.conectar() as conn:
        linha = conn.execute("SELECT 1 AS ok FROM posts WHERE slug = %s", (slug,)).fetchone()
        return linha is not None


def criar(slug, id_user, title, description, icon, status, sections):
    """Insere o post e as seções dele na mesma transação."""
    with usuarios_repo.conectar() as conn:  # commit ao sair; rollback se der erro
        novo = conn.execute(
            """
            INSERT INTO posts (id_user, slug, title, description, icon, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_post
            """,
            (id_user, slug, title, description, icon, status),
        ).fetchone()
        _gravar_secoes(conn, novo["id_post"], sections)


def atualizar(slug, title, description, icon, status, sections):
    """Atualiza o post e troca todas as seções pelas novas (mesma transação).
    O slug e o autor não mudam na edição."""
    with usuarios_repo.conectar() as conn:
        post = conn.execute(
            """
            UPDATE posts
            SET title = %s, description = %s, icon = %s, status = %s
            WHERE slug = %s
            RETURNING id_post
            """,
            (title, description, icon, status, slug),
        ).fetchone()
        if post is None:
            return
        conn.execute("DELETE FROM post_sections WHERE id_post = %s", (post["id_post"],))
        _gravar_secoes(conn, post["id_post"], sections)


def excluir(slug):
    """Apaga o post; as seções (e o progresso de leitura) saem junto, por ON DELETE CASCADE."""
    with usuarios_repo.conectar() as conn:
        conn.execute("DELETE FROM posts WHERE slug = %s", (slug,))
