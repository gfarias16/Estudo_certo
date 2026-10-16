# Versões

## 0.2.0 — Catálogo ampliado e temas — 16/10/2026

240 novas questões: 120 diretas/práticas e 120 análises de duas assertivas.
Total de 300, preservando as 60 anteriores e seu histórico. Correções de assertivas
retornam ambas as referências. Não há alteração de esquema do banco.

Tema escuro inicial e opção clara persistente por navegador, disponíveis no login,
desktop e celular. Repositório público preparado com auditoria do índice e exclusão
de ambientes, bases, autenticação, artefatos e PDFs originais.

Validação local: 26 testes Django (24 aprovados; dois exigem PostgreSQL), Ruff,
migrations, OpenAPI, tipos, build, ESLint, dois testes Vitest e três fluxos Playwright.
Conferência visual dos dois temas no desktop e celular; wheel contém o catálogo CSV.

A primeira CI revelou diferença de limite de `PositiveSmallIntegerField` entre SQLite
e PostgreSQL no OpenAPI. Os serializers agora descrevem o limite portátil de 32767;
schema e tipos foram regenerados, sem migration ou alteração de dados.

CI em PostgreSQL aprovada: 26 testes Django, contrato e frontend, incluindo três testes
de navegador. Supabase atualizado para 300 questões, sem alterar o histórico anterior;
privacidade verificada. Banco com aproximadamente 12,8 MiB, mantendo o plano gratuito.
Build remoto READY e temas verificados no navegador hospedado. O fluxo autenticado
completo online continua como conferência manual, sem inserir dados fictícios no banco real.

## 0.1.0 — MVP local e produção — 15/10/2026

Sistema de estudo com 60 questões, correção por alternativa e artigo/página, revisão de erros e acompanhamento de desempenho.

Correção local: o HTML passa a ser relido em desenvolvimento após um novo build, evitando referências a JavaScript e CSS removidos. Verificação: configuração Django válida; HTML igual ao build em disco; assets respondendo 200; releitura do template após alteração validada.

Fluxo confirmado no Chrome: tela de login, autenticação, catálogo de 60 questões e recarregamento, sem erros JavaScript/HTTP. Nenhuma resposta foi registrada nessa verificação.

Publicado em https://estudo-certo-omega.vercel.app, com PostgreSQL no Supabase. Migrations, catálogo, conta e duas respostas locais preparados; privacidade das tabelas verificada. O banco local foi preservado.

Build remoto corrigido com descoberta explícita dos pacotes Python e dependências lidas de `requirements.txt`. Tela de login desktop/mobile, health, sessão anônima e bloqueio da API privada validados na hospedagem. O fluxo autenticado completo online permanece para teste manual; não foram criados dados fictícios de estudo no banco remoto.
