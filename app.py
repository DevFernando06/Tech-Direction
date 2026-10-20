import re
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "troque-esta-chave-em-producao"  # necessária para session e flash
app.permanent_session_lifetime = timedelta(days=30)  # usado no "Lembrar de mim"

# "Banco de dados" hardcodado na memória
usuarios = []

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TAMANHO_MIN_SENHA = 8

# Trilhas disponíveis (slug na URL -> título)
TRILHAS = {
    "html-css": "HTML & CSS",
    "javascript": "JavaScript",
    "react": "React",
}


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
    return {"usuario_nome": nome, "usuario_iniciais": iniciais(nome)}


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

    usuarios.append({
        "id": len(usuarios) + 1,
        "nome": nome,
        "email": email,
        "data_nascimento": data_nasc,
        "senha_hash": generate_password_hash(senha),
    })
    flash("Conta criada com sucesso! Faça login.", "sucesso")
    return redirect(url_for("login"))


# ---------- ÁREA LOGADA ----------
@app.get("/dashboard")
@login_obrigatorio
def dashboard():
    nome = session["nome"]
    return render_template("trilhas/dashboard.html", nome=nome, primeiro_nome=nome.split()[0])


# url_for('view_trilha') -> /trilha (abre a primeira trilha)
# url_for('view_trilha', slug='react') -> /trilha/react
@app.get("/trilha", defaults={"slug": None})
@app.get("/trilha/<slug>")
@login_obrigatorio
def view_trilha(slug):
    slug = slug or next(iter(TRILHAS))
    if slug not in TRILHAS:
        abort(404)
    return render_template("trilhas/view_trilha.html", slug=slug, titulo=TRILHAS[slug])


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
    return jsonify(ok=True, mensagem="Se houver uma conta associada a este e-mail, enviamos o link de recuperação.")


# ---------- TRILHAS: busca e cadastro ----------
@app.get("/trilhas")
@login_obrigatorio
def search_trilha():
    q = request.args.get("q", "").strip()
    trilhas = {slug: titulo for slug, titulo in TRILHAS.items() if q.lower() in titulo.lower()}
    return render_template("trilhas/search_trilha.html", trilhas=trilhas, q=q)


@app.get("/trilhas/nova")
@login_obrigatorio
def cad_trilha():
    # O POST (salvar a trilha) entra quando o formulário dessa página estiver pronto
    return render_template("admin/cad_trilha.html")


# ---------- ESCRITORES ----------
@app.get("/escritores")
@login_obrigatorio
def writers():
    return render_template("escritores/writers.html")


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
    return render_template("perfil/perfil.html", usuario=usuario)


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
