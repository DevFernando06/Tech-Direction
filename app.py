import os
import re
import uuid
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

UPLOAD_POSTS_DIR = os.path.join("static", "uploads", "posts")
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "svg"}

app = Flask(__name__)
app.secret_key = "troque-esta-chave-em-producao"  # necessária para session e flash
app.permanent_session_lifetime = timedelta(days=30)  # usado no "Lembrar de mim"

app.config["MODO_DEV_SEM_LOGIN"] = True        # Se True, ignora login e senha

# "Banco de dados" hardcodado na memória

usuarios = [
    {
        "id": 1,
        "nome": "admin",
        "email": "teste@teste.com",
        "senha_hash": generate_password_hash("123456"),
    }
]

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TAMANHO_MIN_SENHA = 8

# Posts armazenados em memória até a integração com o PostgreSQL
POSTS = {}


def gerar_slug(texto):
    slug = re.sub(r"[^a-z0-9]+", "-", texto.strip().lower()).strip("-")
    return slug or f"post-{len(POSTS) + 1}"


def buscar_por_email(email):
    email = email.strip().lower()
    return next((u for u in usuarios if u["email"] == email), None)


def buscar_por_id(usuario_id):
    return next((u for u in usuarios if u["id"] == usuario_id), None)


def iniciais(nome):
    partes = nome.split()
    if not partes:
        return ""
    if len(partes) == 1:
        return partes[0][0].upper()
    return (partes[0][0] + partes[-1][0]).upper()


@app.context_processor
def injetar_usuario():
    """Deixa o nome e as iniciais disponíveis em TODOS os templates (header, sidebar...)."""
    nome = session.get("nome", "")
    return {"usuario_nome": nome, "usuario_iniciais": iniciais(nome),"modo_dev_sem_login": app.config.get("MODO_DEV_SEM_LOGIN", False),}


def login_obrigatorio(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Faça login para acessar essa página.", "erro")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return wrapper


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
        session.permanent = lembrar  # True = sessão dura 30 dias
        return redirect(url_for("dashboard"))

    # Mensagem genérica: não revela se o erro foi no e-mail ou na senha
    flash("E-mail ou senha inválidos.", "erro")
    return redirect(url_for("login"))


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
        erro = "Você precisa aceitar os Termos de Uso e a Política de Privacidade."
    elif buscar_por_email(email):
        erro = "Esse e-mail já está cadastrado."

    if erro:
        flash(erro, "erro")
        return render_template("login/cad_user.html", dados=dados)

    usuarios.append(
        {
            "id": len(usuarios) + 1,
            "nome": nome,
            "email": email,
            "data_nascimento": data_nasc,
            "senha_hash": generate_password_hash(senha),
        }
    )
    flash("Conta criada com sucesso! Faça login.", "sucesso")
    return redirect(url_for("login"))


# ---------- ÁREA LOGADA ----------
@app.get("/dashboard")
@login_obrigatorio
def dashboard():
    nome = session["nome"]
    return render_template(
        "dashboard.html",
        nome=nome,
        primeiro_nome=nome.split()[0],
        posts=POSTS,
    )


# url_for('view_post') -> /post (abre o primeiro post)
# url_for('view_post', slug='react') -> /post/react
@app.get("/post", defaults={"slug": None})
@app.get("/post/<slug>")
@login_obrigatorio
def view_post(slug):
    if slug is None:
        slug = next(iter(POSTS), None)
        if slug is None:
            return redirect(url_for("search_post"))
    post = POSTS.get(slug)
    if not post:
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
def search_post():
    q = request.args.get("q", "").strip()
    posts = {
        slug: post for slug, post in POSTS.items() if q.lower() in post["title"].lower()
    }
    return render_template("posts/search_post.html", posts=posts, q=q)


@app.get("/posts/novo")
@login_obrigatorio
def cad_post():
    return render_template("posts/cad_post.html")


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


@app.post("/posts/novo")
@login_obrigatorio
def cad_post_post():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    status = request.form.get("status", "true") == "true"

    subtitles = request.form.getlist("section_subtitle[]")
    texts = request.form.getlist("section_text[]")
    imagens = request.files.getlist("section_img[]")

    sections = []
    for idx, text in enumerate(texts, start=1):
        text_clean = text.strip()
        subtitle_clean = subtitles[idx - 1].strip() if idx - 1 < len(subtitles) else ""
        arquivo_img = imagens[idx - 1] if idx - 1 < len(imagens) else None
        url_img = salvar_imagem_secao(arquivo_img)
        if text_clean:
            sections.append(
                {
                    "subtitle": subtitle_clean or None,
                    "text": text_clean,
                    "url_img": url_img,
                    "display_order": len(sections) + 1,
                    "status": True,
                }
            )

    if not title or not sections:
        flash("Informe o título do post e pelo menos uma seção com texto.", "erro")
        return render_template("posts/cad_post.html")

    slug = gerar_slug(title)
    if slug in POSTS:
        slug = f"{slug}-{len(POSTS) + 1}"

    POSTS[slug] = {
        "id_post": len(POSTS) + 1,
        "id_user": session.get("usuario_id", 1),
        "title": title,
        "description": description or None,
        "status": status,
        "sections": sections,
    }

    flash("Post criado com sucesso!", "sucesso")
    return redirect(url_for("view_post", slug=slug))


# ---------- ESCRITORES ----------
@app.get("/escritores")
@login_obrigatorio
def writers():
    return render_template("admin/writers.html")


@app.get("/escritores/novo")
@login_obrigatorio
def cad_writer():
    # O POST (salvar o escritor) entra quando o formulário dessa página estiver pronto
    return render_template("admin/cad_writer.html")


# ---------- PERFIL ----------
@app.get("/perfil")
@login_obrigatorio
def perfil():
    usuario = buscar_por_id(session["usuario_id"])
    return render_template("perfil.html", usuario=usuario)


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
