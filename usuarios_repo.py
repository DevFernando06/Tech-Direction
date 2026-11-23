"""
Acesso ao banco (PostgreSQL) para usuários: usado pelo login e pelo cadastro.

- Só fica ativo se DATABASE_URL estiver definida no .env.
- Sem DATABASE_URL, o app.py continua usando a lista em memória.
- Os dicionários devolvidos têm o MESMO formato da lista em memória
  (id, nome, email, senha_hash, roles, data_nascimento), então o restante
  do app não precisa saber de onde o usuário veio.

Requer: pip install "psycopg[binary]>=3.1"
Tabelas: users, roles, roles_user (migrations 001 a 004).
"""
import os


class EmailJaCadastrado(Exception):
    """E-mail já existe na tabela users (restrição UNIQUE)."""


class BancoIndisponivel(Exception):
    """Não foi possível conectar ao PostgreSQL (servidor fora do ar, URL errada, senha errada...)."""


def configurado():
    return bool(os.getenv("DATABASE_URL"))


def conectar():
    # Import tardio: o app roda sem o psycopg instalado enquanto usar a lista em memória
    import psycopg
    from psycopg.rows import dict_row

    try:
        return psycopg.connect(
            os.environ["DATABASE_URL"], row_factory=dict_row, connect_timeout=5
        )
    except psycopg.OperationalError as erro:
        raise BancoIndisponivel(str(erro).strip()) from erro


# Um usuário + suas roles ativas, no formato usado pelo app.
# Usuário inativo (status = FALSE) não é retornado, logo não consegue logar.
_SELECT_USUARIO = """
    SELECT
        u.id_user    AS id,
        u.name       AS nome,
        u.email      AS email,
        u.password   AS senha_hash,
        u.date_birth AS data_nascimento,
        COALESCE(
            array_agg(r.description::text) FILTER (WHERE r.id_role IS NOT NULL AND r.status),
            ARRAY[]::text[]
        )            AS roles
    FROM users u
    LEFT JOIN roles_user ru ON ru.id_user = u.id_user
    LEFT JOIN roles r       ON r.id_role = ru.id_role
    WHERE {filtro} AND u.status = TRUE
    GROUP BY u.id_user
"""


def buscar_por_email(email):
    email = (email or "").strip().lower()
    with conectar() as conn:
        return conn.execute(
            _SELECT_USUARIO.format(filtro="u.email = %s"), (email,)
        ).fetchone()


def buscar_por_id(usuario_id):
    if usuario_id is None:
        return None
    with conectar() as conn:
        return conn.execute(
            _SELECT_USUARIO.format(filtro="u.id_user = %s"), (usuario_id,)
        ).fetchone()


def criar_usuario(nome, email, data_nascimento, senha_hash, roles=("student",)):
    """Insere o usuário e suas roles na mesma transação. Devolve o usuário criado."""
    import psycopg

    email = email.strip().lower()
    try:
        with conectar() as conn:  # commit automático ao sair; rollback se der erro
            novo = conn.execute(
                """
                INSERT INTO users (name, email, password, date_birth)
                VALUES (%s, %s, %s, %s)
                RETURNING id_user
                """,
                (nome, email, senha_hash, data_nascimento),
            ).fetchone()
            for role in roles:
                conn.execute(
                    """
                    INSERT INTO roles_user (id_user, id_role)
                    SELECT %s, id_role FROM roles WHERE description = %s
                    """,
                    (novo["id_user"], role),
                )
    except psycopg.errors.UniqueViolation as erro:
        raise EmailJaCadastrado(email) from erro

    return buscar_por_id(novo["id_user"])
