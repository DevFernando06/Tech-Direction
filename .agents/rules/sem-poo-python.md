# Regra: Python Funcional / Procedural (Sem Programação Orientada a Objetos)

Para manter a simplicidade e a consistência com a arquitetura atual do projeto (`app.py`, `usuarios_repo.py`, `posts_repo.py` e `banco.py`), **não utilize Programação Orientada a Objetos (POO)** no código Python da aplicação.

## Diretrizes Obrigatórias

1. **Não crie classes de domínio, serviços ou repositórios:**
   - Evite `class Usuario:`, `class PostService:`, `class BaseRepository:` ou padrões similares (MVC/DDD com classes, dataclasses de entidade ou métodos de instância).
   - Organize o código em **módulos com funções puras e diretas** (ex.: `buscar_por_email(email)`, `criar_post(...)`).

2. **Representação de dados:**
   - Utilize estruturas nativas do Python (`dict`, `list`, `tuple`, `set`) para representar entidades e payloads (mantendo o formato de dicionários compartilhado entre o modo em memória e o PostgreSQL).

3. **Exceções permitidas (casos pontuais da linguagem):**
   - Definição de exceções customizadas simples herdando de `Exception` (ex.: `class EmailJaCadastrado(Exception): ...`).
   - Enums de constantes herdando de `StrEnum`/`Enum` (ex.: `Permissions` em `permissions.py`).

4. **Controle de fluxo e estado:**
   - Prefira funções pequenas, composição de funções e passagem explícita de parâmetros em vez de estado mutável encapsulado em `self`.
