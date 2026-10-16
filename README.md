# Estudo Certo

Sistema privado para estudar o Estatuto da Guarda Municipal de São Gonçalo.
Questões autorais, comentários por alternativa, caderno de erros e painel de desempenho.

**Acesso online:** https://estudo-certo-omega.vercel.app.

**Código:** https://github.com/gfarias16/Estudo_certo.

## Executar no Windows

Requisitos: Python 3.12 e Node.js 24. Na raiz, pelo PowerShell:

Para conferir a origem do catálogo, coloque os três PDFs originais em `docs/`,
conforme [fontes e critérios](docs/contexto/fontes-e-criterios.md). Eles não acompanham o repositório.
Sem os PDFs, `import_catalog` importa o catálogo já conferido; `--verify-sources` exige os originais.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py import_catalog --verify-sources
.\.venv\Scripts\python.exe manage.py create_student estudante --name Estudante
npm.cmd --prefix frontend ci
python scripts/build_frontend.py
.\.venv\Scripts\python.exe manage.py runserver
```

Abra **http://127.0.0.1:8000**. A senha é definida de forma interativa e oculta.
Não sobrescreva um `.env` existente. A instalação atual pode já estar preparada; consulte o status.

Para atualização automática, mantenha Django na porta 8000 e execute, em outro terminal,
`npm.cmd --prefix frontend run dev`. Abra **http://127.0.0.1:5173**.

## V1

- 300 questões em oito temas do estatuto de 2026.
- Tema escuro inicial, com opção de tema claro salva neste navegador.
- Quatro alternativas, correção no servidor e referência ao artigo/página.
- Revisão de erros sem apagar histórico.
- Aproveitamento geral, primeiro contato, cobertura e evolução.
- Diretriz inicial de 30 minutos diários, ajustável na conta.
- Login privado e troca de senha; sem cadastro público.
- Administração de conteúdo em `/admin/`, para contas com permissão.

O catálogo cobre uma seleção de dispositivos, não todo o estatuto ou edital.
Os PDFs originais ficam em `docs/`, sem download público pela aplicação.

## Documentação

- [Comandos](docs/COMANDOS.md)
- [Arquitetura](docs/ARQUITETURA.MD)
- [Estado e pendências](docs/STATUS.md)
- [Versões e validação](docs/VERSÃO.md)
- [Fontes e critérios](docs/contexto/fontes-e-criterios.md)
- [Publicação e backup](docs/procedimentos/publicacao.md)
- [GitHub, exclusões e GitHub Desktop](docs/procedimentos/github.md)

## Hospedagem

Django + React publicados na Vercel, com PostgreSQL no Supabase.
Ambiente local usa SQLite independente; novas respostas não são sincronizadas entre os ambientes.
Não há chamadas pagas de IA durante o estudo.
