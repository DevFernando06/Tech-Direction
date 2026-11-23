"""
Cria o primeiro usuário (admin) no banco, já com a senha em hash.
Uso:  python criar_admin.py "Nome" email@dominio.com SenhaComPeloMenos8
Requer DATABASE_URL no .env e as migrations 001 a 004 já aplicadas.
"""
import sys
from datetime import date

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()
import usuarios_repo  # depois do load_dotenv, para enxergar o DATABASE_URL

if not usuarios_repo.configurado():
    sys.exit("Defina DATABASE_URL no .env antes de rodar.")
if len(sys.argv) != 4 or len(sys.argv[3]) < 8:
    sys.exit('Uso: python criar_admin.py "Nome" email@dominio.com SenhaComPeloMenos8')

nome, email, senha = sys.argv[1:4]
try:
    usuarios_repo.criar_usuario(
        nome, email, date(2000, 1, 1), generate_password_hash(senha), roles=("admin",)
    )
except usuarios_repo.EmailJaCadastrado:
    sys.exit("Esse e-mail já está cadastrado.")
except usuarios_repo.BancoIndisponivel as erro:
    sys.exit(f"Não consegui conectar ao banco: {erro}")
print(f"Admin criado: {email}")
