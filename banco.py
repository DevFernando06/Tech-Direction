"""
Utilitário do banco de dados.

  python banco.py verificar   -> testa a conexão e confere tabelas, roles e usuários
  python banco.py migrar      -> aplica os arquivos de migrations/ em ordem

As migrations do projeto usam IF NOT EXISTS / ON CONFLICT, então "migrar"
pode ser rodado quantas vezes quiser. Tudo roda em uma transação só:
se alguma migration falhar, nada é aplicado.

Requer DATABASE_URL no .env.
"""
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
import usuarios_repo  # depois do load_dotenv, para enxergar o DATABASE_URL

PASTA_MIGRATIONS = Path(__file__).parent / "migrations"
TABELAS_ESPERADAS = ["users", "roles", "roles_user", "posts", "post_sections", "progress_post"]


def migrar():
    arquivos = sorted(PASTA_MIGRATIONS.glob("*.sql"))
    if not arquivos:
        sys.exit(f"Nenhum arquivo .sql encontrado em {PASTA_MIGRATIONS}")
    with usuarios_repo.conectar() as conn:  # commit ao final; rollback se algo falhar
        for arquivo in arquivos:
            conn.execute(arquivo.read_text(encoding="utf-8-sig"))
            print(f"ok  {arquivo.name}")
    print("Migrations aplicadas.")


def verificar():
    with usuarios_repo.conectar() as conn:
        versao = conn.execute("SELECT version() AS v").fetchone()["v"]
        print("Conexão OK:", versao.split(",")[0])

        existentes = {
            linha["table_name"]
            for linha in conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
        }
        for tabela in TABELAS_ESPERADAS:
            print("ok   " if tabela in existentes else "FALTA", tabela)
        if not set(TABELAS_ESPERADAS) <= existentes:
            print("\nRode: python banco.py migrar")
            return

        roles = [l["description"] for l in conn.execute("SELECT description FROM roles ORDER BY id_role")]
        print("Roles:", ", ".join(roles) or "(nenhuma)")
        total = conn.execute("SELECT count(*) AS n FROM users").fetchone()["n"]
        print("Usuários:", total)
        if total == 0:
            print('\nCrie o primeiro: python criar_admin.py "Seu Nome" seu@email.com SuaSenha123')


if __name__ == "__main__":
    comandos = {"migrar": migrar, "verificar": verificar}
    if len(sys.argv) != 2 or sys.argv[1] not in comandos:
        sys.exit(__doc__)
    if not usuarios_repo.configurado():
        sys.exit("Defina DATABASE_URL no .env antes de rodar (veja o .env.example).")
    try:
        comandos[sys.argv[1]]()
    except usuarios_repo.BancoIndisponivel as erro:
        sys.exit(f"Não consegui conectar ao banco: {erro}")
