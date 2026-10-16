# Estado do projeto

Atualizado em 16/10/2026 — versão 0.2.0.

## Funcionalidades

- 300 questões autorais em oito temas: 60 anteriores preservadas e 240 novas.
- Expansão: 120 questões diretas/práticas e 120 análises de duas assertivas com ambas as referências.
- Login privado, correção fundamentada, caderno de erros, desempenho e meta diária.
- Tema escuro inicial; escolha clara/escura persistente por navegador, inclusive no login e celular.

## Ambientes

- Produção: https://estudo-certo-omega.vercel.app, Django/React na Vercel e PostgreSQL no Supabase.
- Catálogo remoto com 300 questões; histórico existente preservado e acesso das funções
  `anon`/`authenticated` às tabelas Django bloqueado, conforme verificação após a importação.
- Banco remoto: aproximadamente 12,8 MiB após a expansão; plano gratuito mantido.
- Deploy validado: `dpl_4bJSkHFgZKqUzoo8DeqYFu55Ghoh`, código `79843ed`, estado READY.
- Local: SQLite independente em `.local/`, com backup anterior à importação; catálogo atualizado.
  O endereço `http://127.0.0.1:8000/` exige servidor local em execução.

## Código e validação

- Repositório público: https://github.com/gfarias16/Estudo_certo, branch `main`, nesta mesma pasta.
- Código, CI e documentação em commits separados; ambientes, bases, PDFs, autenticação e artefatos excluídos.
- [CI aprovada](https://github.com/gfarias16/Estudo_certo/actions/runs/38945454435): 26 testes
  Django em PostgreSQL isolado, migrations, Ruff, OpenAPI, tipos, ESLint, build,
  dois testes Vitest e três testes Playwright.
- Fluxo local isolado: login, erro, revisão correta, persistência, métricas, meta e celular.
- Hospedagem: login desktop/mobile, tema escuro inicial, alternância e persistência de tema,
  health JSON, sessão anônima e bloqueio da API privada; sem erros JavaScript/HTTP.
- Contrato numérico estabilizado entre SQLite e PostgreSQL; sem migration nesta versão.
- Wheel inclui o catálogo CSV e não inclui ambientes, PDFs ou arquivos privados.

## Pendências e limites

- Conferir manualmente login e uma resposta no domínio público; o fluxo autenticado completo
  foi validado em bancos isolados. Não foram criados estudantes ou respostas de teste no Supabase.
- Definir e validar backup/restauração PostgreSQL; `pg_dump` não está instalado neste ambiente.
- Projetos gratuitos Supabase podem pausar após uma semana sem atividade; cotas seguem aplicáveis.
- Publicação pela CLI; integração Git automática com a Vercel não foi configurada.
- Catálogo cobre uma seleção do estatuto, sem atualização automática por nova lei ou retificação.
- `check --deploy` mantém avisos W005/W021 de HSTS em subdomínios/preload; não habilitados automaticamente.

Novas respostas não são sincronizadas entre SQLite e Supabase. Consulte os procedimentos de
[publicação](procedimentos/publicacao.md) e [GitHub Desktop](procedimentos/github.md).
