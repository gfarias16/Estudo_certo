# Comandos do ESTUDO CERTO

Execute na raiz, pelo PowerShell. Use `npm.cmd` e o Python da `.venv`.

## Instalação

| Comando | Finalidade |
|---|---|
| `python -m venv .venv` | Criar ambiente Python isolado. |
| `.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt` | Instalar dependências e ferramentas de desenvolvimento. |
| `Copy-Item .env.example .env` | Criar configuração, somente se `.env` ainda não existir. |
| `npm.cmd --prefix frontend ci` | Instalar frontend conforme o lockfile. |

## Banco e contas

| Comando | Finalidade |
|---|---|
| `.\.venv\Scripts\python.exe manage.py migrate --plan` | Conferir migrations pendentes. |
| `.\.venv\Scripts\python.exe manage.py migrate` | Aplicar migrations ao banco configurado. |
| `.\.venv\Scripts\python.exe manage.py import_catalog --verify-sources` | Conferir PDFs e importar 300 questões sem duplicação. |
| `.\.venv\Scripts\python.exe manage.py import_catalog --verify-sources --dry-run` | Validar catálogo sem persistir alterações. |
| `.\.venv\Scripts\python.exe manage.py create_student estudante --name Estudante` | Criar estudante com senha interativa e oculta. |
| `.\.venv\Scripts\python.exe manage.py create_student administrador --admin` | Criar conta com acesso ao Django Admin. |
| `.\.venv\Scripts\python.exe manage.py changepassword estudante` | Redefinir senha sem registrá-la nos argumentos. |
| `.\.venv\Scripts\python.exe manage.py harden_database` | Revogar acesso da API pública do Supabase às tabelas Django. |
| `.\.venv\Scripts\python.exe manage.py check_database_privacy` | Verificar privilégios no PostgreSQL/Supabase. |

## Executar

| Comando | Finalidade |
|---|---|
| `python scripts/build_frontend.py` | Instalar pelo lockfile e compilar React para Django/Vercel. |
| `.\.venv\Scripts\python.exe manage.py runserver` | Servir sistema em `127.0.0.1:8000`. |
| `npm.cmd --prefix frontend run dev` | React com atualização automática em `127.0.0.1:5173`; exige Django na porta 8000. |
| `.\.venv\Scripts\python.exe manage.py collectstatic --noinput` | Coletar estáticos para pacote local; Vercel faz a coleta nativa. |

## Validar

| Comando | Finalidade |
|---|---|
| `.\.venv\Scripts\python.exe manage.py check` | Conferir configuração Django. |
| `.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run` | Detectar modelos sem migration. |
| `.\.venv\Scripts\python.exe manage.py test study.tests` | Testar regras, autenticação, catálogo e métricas. |
| `.\.venv\Scripts\python.exe -m ruff check config study content scripts` | Verificar código Python. |
| `npm.cmd --prefix frontend run build` | Verificar TypeScript e gerar pacote de produção. |
| `npm.cmd --prefix frontend run lint` | Revisar React/TypeScript. |
| `npm.cmd --prefix frontend run test` | Testar seleção, confirmação e reenvio de respostas. |
| `npm.cmd --prefix frontend run test:e2e` | Testar fluxo no navegador com banco isolado. |

## Contratos e fontes

| Comando | Finalidade |
|---|---|
| `.\.venv\Scripts\python.exe manage.py spectacular --file frontend/schema.json --validate --fail-on-warn` | Gerar e validar OpenAPI. |
| `npm.cmd --prefix frontend run api:types` | Gerar tipos TypeScript do contrato. |
| `.\.venv\Scripts\python.exe scripts/extract_statute.py` | Extrair texto auxiliar para `.local/`; conferir sempre a imagem. |

## Preparação do Supabase

Os comandos abaixo leem `.env.production.local` e preservam o `.env` e o SQLite locais.

| Comando | Finalidade |
|---|---|
| `.\.venv\Scripts\python.exe scripts/production.py plan` | Conferir migrations no Supabase antes de aplicá-las. |
| `.\.venv\Scripts\python.exe scripts/production.py migrate` | Aplicar migrations pela conexão de sessão. |
| `.\.venv\Scripts\python.exe scripts/production.py seed` | Conferir PDFs e importar catálogo no Supabase. |
| `.\.venv\Scripts\python.exe scripts/production.py privacy` | Verificar bloqueio das funções públicas no PostgreSQL remoto. |
| `.\.venv\Scripts\python.exe scripts/production.py harden` | Revogar privilégios das funções públicas sobre as tabelas Django. |
| `.\.venv\Scripts\python.exe scripts/production.py check` | Verificar configurações Django de produção. |
| `.\.venv\Scripts\python.exe scripts/production.py backup` | Gerar backup do Supabase pela conexão de sessão; exige `pg_dump`. |
| `.\.venv\Scripts\python.exe scripts/backup_database.py` | Criar backup do banco configurado no ambiente; PostgreSQL exige `pg_dump`. |

Tela branca local: [diagnóstico e correção](incidentes/2026-10-15-tela-branca-local.md).

Publicação e backup: [procedimento](procedimentos/publicacao.md).


GitHub e auditoria antes de commits: [procedimento](procedimentos/github.md).
