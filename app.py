import os
import re
import uuid
from permissions import Permissions
from roles import validate_access
from datetime import date, datetime, timedelta
from functools import wraps

from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

import usuarios_repo
import posts_repo

UPLOAD_POSTS_DIR = os.path.join("static", "uploads", "posts")
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "svg"}

load_dotenv()  # lê o arquivo .env (SECRET_KEY, MODO_DEV_SEM_LOGIN e DATABASE_URL)

app = Flask(__name__)
# Em produção, defina SECRET_KEY no .env; o valor padrão serve apenas para desenvolvimento
app.secret_key = os.getenv("SECRET_KEY", "troque-esta-chave-em-producao")  # necessária para session e flash
app.permanent_session_lifetime = timedelta(days=30)  # usado no "Lembrar de mim"

app.config["MODO_DEV_SEM_LOGIN"] = os.getenv("MODO_DEV_SEM_LOGIN", "0") == "1"  # Se True, ignora login e senha

# True se DATABASE_URL estiver no .env: login e cadastro passam a usar o PostgreSQL
USAR_BANCO = usuarios_repo.configurado()

# "Banco de dados" e usuários de TESTE, SEM CONEXÃO COM BD

SENHA_PADRAO = generate_password_hash("12345678")

usuarios = [
    {"id": 1, "nome": "admin", "email": "teste@teste.com",
     "senha_hash": generate_password_hash("123456"), "roles": ["admin"]},
    {"id": 2, "nome": "Mariana Vasconcelos", "email": "mariana@techdirection.edu",
     "senha_hash": SENHA_PADRAO, "roles": ["writer"]},
    {"id": 3, "nome": "Carlos Mendes", "email": "carlos@techdirection.edu",
     "senha_hash": SENHA_PADRAO, "roles": ["writer"]},
    {"id": 4, "nome": "Lucas Silva", "email": "lucas@techdirection.edu",
     "senha_hash": SENHA_PADRAO, "roles": ["student"]},
]

#role foi adicionado aos usuários para verificar autorização de acesso!

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TAMANHO_MIN_SENHA = 8

# Posts armazenados em memória até a integração com o PostgreSQL
POSTS = {}

POST_ICONS = [
    ("bi-code-slash", "Código / Web"),
    ("bi-layers", "Camadas / Arquitetura"),
    ("bi-stars", "Destaque / Framework"),
    ("bi-terminal", "Terminal / CLI"),
    ("bi-database", "Banco de Dados"),
    ("bi-braces", "Lógica / Programação"),
    ("bi-cpu", "Hardware / CPU"),
    ("bi-robot", "Inteligência Artificial"),
    ("bi-globe", "Web / Redes"),
    ("bi-shield-check", "Segurança"),
    ("bi-phone", "Mobile"),
    ("bi-git", "Git / Versionamento"),
    ("bi-book", "Guia / Fundamentos"),
]
POST_ICON_IDS = {icone for icone, _ in POST_ICONS}


def icone_valido(icone):
    return icone if icone in POST_ICON_IDS else POST_ICONS[0][0]


def gerar_slug(texto):
    slug = re.sub(r"[^a-z0-9]+", "-", texto.strip().lower()).strip("-")
    return slug or f"post-{len(POSTS) + 1}"


def proximo_id_post():
    return max((p["id_post"] for p in POSTS.values()), default=0) + 1


def listar_posts():
    return posts_repo.listar() if USAR_BANCO else POSTS


def buscar_post(slug):
    return posts_repo.buscar(slug) if USAR_BANCO else POSTS.get(slug)


def slug_existe(slug):
    return posts_repo.slug_existe(slug) if USAR_BANCO else slug in POSTS


def slug_unico(titulo):
    base = gerar_slug(titulo)
    slug, n = base, 2
    while slug_existe(slug):
        slug = f"{base}-{n}"
        n += 1
    return slug


def buscar_por_email(email):
    if USAR_BANCO:
        return usuarios_repo.buscar_por_email(email)
    email = email.strip().lower()
    return next((u for u in usuarios if u["email"] == email), None)


def buscar_por_id(usuario_id):
    if USAR_BANCO:
        return usuarios_repo.buscar_por_id(usuario_id)
    return next((u for u in usuarios if u["id"] == usuario_id), None)


def nome_autor(post):
    if post.get("autor_nome"):
        return post["autor_nome"]
    autor = buscar_por_id(post["id_user"])
    return autor["nome"] if autor else "Desconhecido"


def iniciais(nome):
    partes = nome.split()
    if not partes:
        return ""
    if len(partes) == 1:
        return partes[0][0].upper()
    return (partes[0][0] + partes[-1][0]).upper()

def roles_do_usuario(): # retorna o papél do usuário (roles)
    return session.get("roles", []) 

def pode(permissao):  # verifica se o usuário tem a permissão necessária
    return validate_access(roles_do_usuario(), permissao) 

def e_autor(post): # verifica se um post é do usuário logado
    return post["id_user"] == session.get("usuario_id")

def pode_editar_post(post):
    return pode(Permissions.UPDATE_ANY_POST) or (
        pode(Permissions.UPDATE_POST) and e_autor(post)
    ) # define se o usuário pode editar post (se ele for autor do post ou adm)

def pode_excluir_post(post):
    return pode(Permissions.DELETE_ANY_POST) or (
        pode(Permissions.DELETE_POST) and e_autor(post)
    ) # define se o usuário pode excluir um post (autor ou admin)

def pode_ver_post(post):
    if not pode(Permissions.READ_POST):
        return False
    return post["status"] or pode_editar_post(post)
    # rescunho = status false; apenas o autor/admin podem ver  



@app.context_processor
def injetar_usuario():
    """Deixa o nome e as iniciais disponíveis em TODOS os templates (header, sidebar...)."""
    nome = session.get("nome", "")
    return {
        "usuario_logado": "usuario_id" in session,
        "usuario_nome": nome,
        "usuario_iniciais": iniciais(nome),
        "modo_dev_sem_login": app.config.get("MODO_DEV_SEM_LOGIN", False),
        "pode": pode,
        "pode_editar_post": pode_editar_post,
        "pode_excluir_post": pode_excluir_post,
        "nome_autor": nome_autor,
    }

@app.errorhandler(usuarios_repo.BancoIndisponivel)
def banco_indisponivel(erro):
    """Banco fora do ar: mostra aviso na própria tela em vez de erro 500."""
    app.logger.error("Banco de dados indisponível: %s", erro)
    flash("Não foi possível acessar o banco de dados agora. Tente novamente em instantes.", "erro")
    if request.endpoint == "cad_user_post":
        dados = {
            "userName": request.form.get("userName", "").strip(),
            "userEmail": request.form.get("userEmail", "").strip().lower(),
            "dateBirth": request.form.get("dateBirth", ""),
        }
        return render_template("login/cad_user.html", dados=dados), 503
    return render_template("login/login.html", email=request.form.get("login", "")), 503


def login_obrigatorio(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Faça login para acessar essa página.", "erro")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def permissao_obrigatoria(permissao):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not pode(permissao):
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.get("/")
def index():
    return redirect(url_for("login"))


# ---------- LOGIN ----------
@app.get("/login")
def login():
    return render_template("login/login.html")


@app.post("/login")

def login_post():
    if app.config.get("MODO_DEV_SEM_LOGIN"):
        session.clear()
        session["usuario_id"] = 1
        session["nome"] = "admin"
        session["roles"] = ["admin"]
        return redirect(url_for("dashboard"))

# ---- fluxo normal (só roda se MODO_DEV_SEM_LOGIN = False) ----

    # O campo se chama "login", mas no formulário agora o valor é o e-mail
    email = request.form.get("login", "").strip().lower()
    senha = request.form.get("password", "")
    lembrar = request.form.get("remember") is not None

    usuario = buscar_por_email(email)
    if usuario and check_password_hash(usuario["senha_hash"], senha):
        session.clear()
        session["usuario_id"] = usuario["id"]
        session["nome"] = usuario["nome"]
        session["roles"] = usuario["roles"] 
        session.permanent = lembrar  # True = sessão dura 30 dias
        return redirect(url_for("dashboard"))

    # Mensagem genérica: não revela se o erro foi no e-mail ou na senha
    flash("E-mail ou senha inválidos.", "erro")
    return render_template("login/login.html", email=email), 401  # mantém o e-mail digitado


# ---------- CADASTRO ----------
@app.get("/cadastro")
def cad_user():
    dados = {"userName": "", "userEmail": "", "dateBirth": ""}
    return render_template("login/cad_user.html", dados=dados)


@app.post("/cadastro")
def cad_user_post():
    nome = request.form.get("userName", "").strip()
    email = request.form.get("userEmail", "").strip().lower()
    data_nasc_str = request.form.get("dateBirth", "")
    senha = request.form.get("password", "")
    aceitou_termos = request.form.get("terms") is not None

    # Mantém o que a pessoa digitou se der erro, menos a senha (por segurança)
    dados = {"userName": nome, "userEmail": email, "dateBirth": data_nasc_str}

    try:
        data_nasc = datetime.strptime(data_nasc_str, "%Y-%m-%d").date()
    except ValueError:
        data_nasc = None

    erro = None
    if not all([nome, email, data_nasc_str, senha]):
        erro = "Preencha todos os campos."
    elif not EMAIL_REGEX.match(email):
        erro = "E-mail inválido."
    elif data_nasc is None or data_nasc >= date.today():
        erro = "Data de nascimento inválida."
    elif len(senha) < TAMANHO_MIN_SENHA:
        erro = f"A senha deve ter pelo menos {TAMANHO_MIN_SENHA} caracteres."
    elif not aceitou_termos:
        erro = "Você precisa aceitar a Política de Privacidade."
    elif buscar_por_email(email):
        erro = "Esse e-mail já está cadastrado."

    if erro:
        flash(erro, "erro")
        return render_template("login/cad_user.html", dados=dados)

    senha_hash = generate_password_hash(senha)
    if USAR_BANCO:
        try:
            usuarios_repo.criar_usuario(nome, email, data_nasc, senha_hash)
        except usuarios_repo.EmailJaCadastrado:
            flash("Esse e-mail já está cadastrado.", "erro")
            return render_template("login/cad_user.html", dados=dados)
    else:
        usuarios.append(
            {
                "id": len(usuarios) + 1,
                "nome": nome,
                "email": email,
                "data_nascimento": data_nasc,
                "senha_hash": senha_hash,
                "roles": ["student"],
            }
        )
    flash("Conta criada com sucesso! Faça login.", "sucesso")
    return redirect(url_for("login"))


# ---------- ÁREA LOGADA ----------
@app.get("/dashboard")
@login_obrigatorio
def dashboard():
    nome = session["nome"]
    posts_visiveis = {s: p for s, p in listar_posts().items() if pode_ver_post(p)}
    autores = {p["id_user"]: nome_autor(p) for p in posts_visiveis.values()}
    return render_template(
        "dashboard.html",
        nome=nome,
        primeiro_nome=nome.split()[0],
        posts=posts_visiveis,
        autores=autores,
    )


# url_for('view_post') -> /post (abre o primeiro post)
# url_for('view_post', slug='react') -> /post/react
@app.get("/post", defaults={"slug": None})
@app.get("/post/<slug>")
@login_obrigatorio
def view_post(slug):
    if slug is None:
        slug = next((s for s, p in listar_posts().items() if pode_ver_post(p)), None)
        if slug is None:
            return redirect(url_for("search_post") if pode(Permissions.CREATE_POST) else url_for("dashboard"))
    post = buscar_post(slug)
    if not post or not pode_ver_post(post):
        abort(404)
    return render_template("posts/view_post.html", slug=slug, post=post, titulo=post["title"])


# ---------- RECUPERAR SENHA (modal do login) ----------
@app.post("/recuperar-senha")
def recuperar_senha():
    dados = request.get_json(silent=True) or request.form
    email = (dados.get("recoveryEmail") or "").strip().lower()

    if not EMAIL_REGEX.match(email):
        return jsonify(ok=False, mensagem="Informe um e-mail válido."), 400

    if buscar_por_email(email):
        # Aqui entraria o envio do e-mail com o link de redefinição.
        pass

    # Resposta igual exista a conta ou não: não revela quais e-mails estão cadastrados
    return jsonify(
        ok=True,
        mensagem="Se houver uma conta associada a este e-mail, enviamos o link de recuperação.",
    )


# ---------- POSTS: busca e cadastro ----------
@app.get("/posts")
@login_obrigatorio
@permissao_obrigatoria(Permissions.CREATE_POST)
def search_post():
    q = request.args.get("q", "").strip()
    posts = {
        slug: post for slug, post in listar_posts().items() 
        if pode_ver_post(post) and q.lower() in post["title"].lower()
    }
    return render_template("posts/search_post.html", posts=posts, q=q)


@app.get("/posts/novo")
@login_obrigatorio
@permissao_obrigatoria(Permissions.CREATE_POST)
def cad_post():
    return render_template("posts/cad_post.html", icones=POST_ICONS)


def salvar_imagem_secao(arquivo):
    if not arquivo or not arquivo.filename:
        return None
    nome_seguro = secure_filename(arquivo.filename)
    ext = nome_seguro.rsplit(".", 1)[-1].lower() if "." in nome_seguro else ""
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return None
    pasta_destino = os.path.join(app.root_path, UPLOAD_POSTS_DIR)
    os.makedirs(pasta_destino, exist_ok=True)
    nome_unico = f"{uuid.uuid4().hex}_{nome_seguro}"
    arquivo.save(os.path.join(pasta_destino, nome_unico))
    return url_for("static", filename=f"uploads/posts/{nome_unico}")

def montar_secoes(form, files):
    subtitles = form.getlist("section_subtitle[]")
    texts = form.getlist("section_text[]")
    imagens = files.getlist("section_img[]")
    imagens_atuais = form.getlist("section_img_atual[]")

    sections = []
    for idx, text in enumerate(texts):
        text_clean = text.strip()
        if not text_clean:
            continue

        subtitle_clean = subtitles[idx].strip() if idx < len(subtitles) else ""
        arquivo_img = imagens[idx] if idx < len(imagens) else None
        url_img = salvar_imagem_secao(arquivo_img)

        # Sem imagem nova: mantém a que já existia (só aceita caminhos da nossa pasta)
        if url_img is None and idx < len(imagens_atuais):
            atual = imagens_atuais[idx]
            if atual.startswith("/static/uploads/posts/"):
                url_img = atual

        sections.append(
            {
                "subtitle": subtitle_clean or None,
                "text": text_clean,
                "url_img": url_img,
                "display_order": len(sections) + 1,
                "status": True,
            }
        )
    return sections

@app.post("/posts/novo")
@login_obrigatorio
@permissao_obrigatoria(Permissions.CREATE_POST)
def cad_post_post():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    icon = icone_valido(request.form.get("icon", "").strip())
    status = request.form.get("status", "true") == "true"
    sections = montar_secoes(request.form, request.files)

    if not title or not sections:
        flash("Informe o título do post e pelo menos uma seção com texto.", "erro")
        return render_template("posts/cad_post.html", icones=POST_ICONS)

    slug = slug_unico(title)

    if USAR_BANCO:
        posts_repo.criar(
            slug, session.get("usuario_id", 1), title, description or None, icon, status, sections
        )
    else:
        POSTS[slug] = {
            "id_post": proximo_id_post(),
            "id_user": session.get("usuario_id", 1),
            "title": title,
            "description": description or None,
            "icon": icon,
            "status": status,
            "sections": sections,
        }

    flash("Post criado com sucesso!", "sucesso")
    return redirect(url_for("view_post", slug=slug))

@app.get("/post/<slug>/editar")
@login_obrigatorio
def edit_post(slug):
    post = buscar_post(slug)
    if not post or not pode_ver_post(post):
        abort(404)
    if not pode_editar_post(post):
        abort(403)
    return render_template("posts/cad_post.html", slug=slug, post=post, icones=POST_ICONS)


@app.post("/post/<slug>/editar")
@login_obrigatorio
def edit_post_post(slug):
    post = buscar_post(slug)
    if not post or not pode_ver_post(post):
        abort(404)
    if not pode_editar_post(post):
        abort(403)

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    icon = icone_valido(request.form.get("icon", "").strip())
    status = request.form.get("status", "true") == "true"
    sections = montar_secoes(request.form, request.files)

    if not title or not sections:
        flash("Informe o título do post e pelo menos uma seção com texto.", "erro")
        return render_template("posts/cad_post.html", slug=slug, post=post, icones=POST_ICONS)

    if USAR_BANCO:
        posts_repo.atualizar(slug, title, description or None, icon, status, sections)
    else:
        post["title"] = title
        post["description"] = description or None
        post["icon"] = icon
        post["status"] = status
        post["sections"] = sections

    flash("Post atualizado com sucesso!", "sucesso")
    return redirect(url_for("view_post", slug=slug))

@app.post("/post/<slug>/excluir")
@login_obrigatorio
def excluir_post(slug):
    post = buscar_post(slug)
    if not post or not pode_ver_post(post):
        abort(404)
    if not pode_excluir_post(post):
        abort(403)
    if USAR_BANCO:
        posts_repo.excluir(slug)
    else:
        del POSTS[slug]
    flash("Post excluído com sucesso!", "sucesso")
    return redirect(url_for("search_post"))


# ---------- ESCRITORES ----------
@app.get("/escritores")
@login_obrigatorio
@permissao_obrigatoria(Permissions.MANAGE_WRITERS)
def writers():
    if USAR_BANCO:
        escritores = usuarios_repo.listar_por_role("writer")
    else:
        escritores = [u for u in usuarios if "writer" in u["roles"]]
    todos_posts = list(listar_posts().values())
    posts_por_autor = {
        u["id"]: sum(1 for p in todos_posts if p["id_user"] == u["id"])
        for u in escritores
    }
    return render_template(
        "admin/writers.html",
        escritores=escritores,
        posts_por_autor=posts_por_autor,
    )


@app.post("/escritores/<int:id_usuario>/remover")
@login_obrigatorio
@permissao_obrigatoria(Permissions.MANAGE_WRITERS)
def remover_writer(id_usuario):
    usuario = buscar_por_id(id_usuario)
    if not usuario:
        abort(404)
    if "writer" in usuario["roles"]:
        if USAR_BANCO:
            usuarios_repo.remover_role(usuario["id"], "writer")
        else:
            usuario["roles"].remove("writer")
            if not usuario["roles"]:
                usuario["roles"].append("student")
        flash(f"Papel de escritor removido de {usuario['nome']}.", "sucesso")
    return redirect(url_for("writers"))


@app.get("/escritores/novo")
@login_obrigatorio
@permissao_obrigatoria(Permissions.MANAGE_WRITERS)
def cad_writer():
    if USAR_BANCO:
        candidatos = usuarios_repo.listar_candidatos_escritor()
    else:
        candidatos = [
            u for u in usuarios if "writer" not in u["roles"] and "admin" not in u["roles"]
        ]
    return render_template("admin/cad_writer.html", candidatos=candidatos)


@app.post("/escritores/novo")
@login_obrigatorio
@permissao_obrigatoria(Permissions.MANAGE_WRITERS)
def cad_writer_post():
    user_id = request.form.get("user_id", type=int)
    usuario = buscar_por_id(user_id)
    if not usuario or "admin" in usuario["roles"]:
        flash("Selecione um usuário válido.", "erro")
        return redirect(url_for("cad_writer"))

    if "writer" not in usuario["roles"]:
        if USAR_BANCO:
            usuarios_repo.adicionar_role(usuario["id"], "writer")
        else:
            usuario["roles"].append("writer")
    flash(f"{usuario['nome']} agora é escritor(a)!", "sucesso")
    return redirect(url_for("writers"))


# ---------- PERFIL ----------
@app.get("/perfil")
@login_obrigatorio
def perfil():
    usuario = buscar_por_id(session["usuario_id"])
    return render_template("perfil.html", usuario=usuario)


@app.post("/perfil")
@login_obrigatorio
def perfil_post():
    usuario = buscar_por_id(session["usuario_id"])
    if not usuario:
        abort(404)

    nome = request.form.get("userName", "").strip()
    email = request.form.get("userEmail", "").strip().lower()
    data_nasc_str = request.form.get("dateBirth", "")
    senha_atual = request.form.get("currentPassword", "")
    senha_nova = request.form.get("newPassword", "")
    confirmar = request.form.get("confirmNewPassword", "")

    try:
        data_nasc = datetime.strptime(data_nasc_str, "%Y-%m-%d").date()
    except ValueError:
        data_nasc = None

    quer_trocar_senha = any([senha_atual, senha_nova, confirmar])
    outro = buscar_por_email(email) if EMAIL_REGEX.match(email) else None

    # O papel (role) nunca é lido do formulário: só os administradores mudam isso
    erro = None
    if not all([nome, email, data_nasc_str]):
        erro = "Preencha nome, e-mail e data de nascimento."
    elif not EMAIL_REGEX.match(email):
        erro = "E-mail inválido."
    elif data_nasc is None or data_nasc >= date.today():
        erro = "Data de nascimento inválida."
    elif outro and outro["id"] != usuario["id"]:
        erro = "Esse e-mail já está em uso por outra conta."
    elif quer_trocar_senha and not check_password_hash(usuario["senha_hash"], senha_atual):
        erro = "A senha atual está incorreta."
    elif quer_trocar_senha and len(senha_nova) < TAMANHO_MIN_SENHA:
        erro = f"A nova senha deve ter pelo menos {TAMANHO_MIN_SENHA} caracteres."
    elif quer_trocar_senha and senha_nova != confirmar:
        erro = "A confirmação da nova senha não confere."

    nova_hash = generate_password_hash(senha_nova) if quer_trocar_senha and not erro else None

    if not erro:
        if USAR_BANCO:
            try:
                usuarios_repo.atualizar_usuario(usuario["id"], nome, email, data_nasc, nova_hash)
            except usuarios_repo.EmailJaCadastrado:
                erro = "Esse e-mail já está em uso por outra conta."
        else:
            usuario["nome"] = nome
            usuario["email"] = email
            usuario["data_nascimento"] = data_nasc
            if nova_hash:
                usuario["senha_hash"] = nova_hash

    if erro:
        flash(erro, "erro")
        # devolve a tela com o que a pessoa digitou (as senhas nunca voltam preenchidas)
        digitado = {**usuario, "nome": nome, "email": email, "data_nascimento": data_nasc_str}
        return render_template("perfil.html", usuario=digitado), 400

    session["nome"] = nome  # o nome do cabeçalho acompanha a mudança
    flash("Perfil atualizado com sucesso!", "sucesso")
    return redirect(url_for("perfil"))


# ---------- PÁGINAS INSTITUCIONAIS (PÚBLICAS) ----------
@app.get("/quem-somos")
def quem_somos():
    return render_template("quem_somos.html")


@app.get("/politica-de-privacidade")
def politica_privacidade():
    return render_template("politica_privacidade.html")


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
