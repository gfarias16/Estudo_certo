# Estudo Certo — orientação para desenvolvimento

Aplicação privada de estudo: Django 5.2 LTS, DRF, React/TypeScript e Vite.
Fonte normativa da V1: Lei municipal 1.625/2026 em `docs/Estatuto_GMS.pdf`.

## Contexto mínimo

1. Leia `README.md`.
2. Consulte `docs/ARQUITETURA.MD`, `docs/COMANDOS.md` e `docs/STATUS.md` conforme a tarefa.
3. Conteúdo: `docs/contexto/fontes-e-criterios.md`.
4. Interface: `docs/interface/diretrizes-visuais.md`.

## Regras

- Preserve PDFs originais, configuração local, bancos e histórico do estudante.
- Não publique conteúdo com base apenas no OCR; confira o dispositivo na imagem.
- Provas antigas e de Niterói orientam estilo, não fundamentam o estatuto de 2026.
- Não envie gabarito, comentários ou trechos antes da confirmação da resposta.
- Questão respondida exige nova revisão; não altere o conteúdo em lugar.
- Atualize OpenAPI e tipos gerados quando a API mudar.
- Produção exige PostgreSQL. SQLite é apenas local.
- No Supabase, revogue acesso de `anon`/`authenticated` às tabelas Django e verifique a privacidade após migrations.
- Nunca exponha `.env`, senhas, tokens, cookies ou connection strings.
- Não execute operações destrutivas sem autorização explícita.
- Não faça commit/push automaticamente. Este workspace começou sem repositório Git.
- Atualize status e versão quando comportamento ou validação mudar.
- No PowerShell, use `npm.cmd` e o Python da `.venv`, sem alterar a política de execução.

## Validação

Backend: testes Django, Ruff, migrations e OpenAPI.
Frontend: tipos, build, ESLint e Vitest.
Fluxo crítico: Playwright com banco isolado em `.local/e2e.sqlite3`.
Distinga sempre validação local de validação no Supabase/Vercel.
