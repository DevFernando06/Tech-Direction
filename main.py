from flask import Flask, redirect, render_template, request, url_for, abort

app = Flask(__name__,
    static_url_path='',
    static_folder='static')


# ---------------------------------------------------------------------------
# "Banco de dados" em memória
# ---------------------------------------------------------------------------
usuarios = [
    {"id": 1, "nome": "Lucas Silva", "email": "lucas@techdirection.edu",
     "nascimento": "2000-05-10", "roles": ["student"]},
    {"id": 2, "nome": "Admin Tech Direction", "email": "admin@techdirection.edu",
     "nascimento": "1990-01-01", "roles": ["admin"]},
    {"id": 3, "nome": "Mariana Vasconcelos", "email": "mariana@techdirection.edu",
     "nascimento": "1992-03-15", "roles": ["writer"]},
    {"id": 4, "nome": "Carlos Mendes", "email": "carlos@techdirection.edu",
     "nascimento": "1989-07-22", "roles": ["writer"]},
    {"id": 5, "nome": "Beatriz Lima", "email": "beatriz@techdirection.edu",
     "nascimento": "1995-11-02", "roles": ["writer"]},
]

trilhas = [
    {
        "id": 1,
        "categoria": "Fundamentos",
        "titulo": "HTML & CSS",
        "descricao": "Entenda como a web é estruturada, estilizada e publicada, com exemplos e referências.",
        "autor": "Equipe Tech Direction",
        "leituras": 6,
        "referencias": 12,
    },
    {
        "id": 2,
        "categoria": "Programação",
        "titulo": "JavaScript",
        "descricao": "Uma introdução visual à linguagem que dá vida à web, com conceitos, imagens e links úteis.",
        "autor": "Marina Lima",
        "leituras": 8,
        "referencias": 15,
    },
    {
        "id": 3,
        "categoria": "Próximo passo",
        "titulo": "React",
        "descricao": "Conheça a biblioteca, seu ecossistema e as ideias por trás de interfaces baseadas em componentes.",
        "autor": "André Costa",
        "leituras": 7,
        "referencias": 10,
    },
]


# ---------------------------------------------------------------------------
# SEM Autenticação (só renderiza as telas)
# ---------------------------------------------------------------------------
@app.get("/")
def home():
    return redirect(url_for("dashboard"))


@app.get("/login")
def login():
    return render_template("login/login.html")


@app.post("/login")
def login_post():
    # Por enquanto não valida nada: qualquer envio vai para o dashboard
    return redirect(url_for("dashboard"))


@app.get("/cadastro")
def cad_user():
    return render_template("login/cad_user.html")


@app.post("/cadastro")
def cad_user_post():
    # Por enquanto não salva nada: volta para o login
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Área logada
# ---------------------------------------------------------------------------
@app.get("/dashboard")
def dashboard():
    return render_template("dashboard.html", trilhas=trilhas)


@app.get("/perfil")
def perfil():
    return render_template("perfil.html", usuario="usuário teste")


# ---------------------------------------------------------------------------
# Trilhas
# ---------------------------------------------------------------------------
@app.get("/trilhas")
def search_trilha():
    termo = request.args.get("q", "").strip().lower()
    resultado = [
        t for t in trilhas
        if not termo or termo in " ".join(  #buscar trilha
            [t["titulo"], t["categoria"], t["descricao"], t["autor"]]
        ).lower()
    ]
    return render_template("trilhas/search_trilha.html", trilhas=resultado, termo=termo)


@app.get("/trilhas/nova")
def cad_trilha():
    return render_template("trilhas/cad_trilha.html")


@app.post("/trilhas/nova")
def cad_trilha_post():
    # Por enquanto não salva nada: volta para a lista de trilhas
    return redirect(url_for("search_trilha"))


# `/trilha` (sem id) existe porque o dashboard chama url_for('view_trilha') sem argumentos.
@app.get("/trilha", defaults={"id": 1})
@app.get("/trilha/<int:id>")
def view_trilha(id):
    trilha = next((t for t in trilhas if t["id"] == id), None)
    if trilha is None:
        abort(404)
    return render_template("trilhas/view_trilha.html", trilha=trilha)


# ---------------------------------------------------------------------------
# Escritores
# ---------------------------------------------------------------------------
@app.get("/escritores")
def writers():
    escritores = [u for u in usuarios if "writer" in u["roles"]]
    return render_template("admin/writers.html", escritores=escritores)


@app.get("/escritores/novo")
def cad_writer():
    return render_template("admin/cad_writer.html")


@app.post("/escritores/novo")
def cad_writer_post():
    # Por enquanto não salva nada: volta para a lista de escritores
    return redirect(url_for("writers"))


if __name__ == "__main__":
    app.run(debug=True)