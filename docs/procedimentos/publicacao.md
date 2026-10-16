# Publicação e backup

Produção: https://estudo-certo-omega.vercel.app.
Projeto Vercel: `estudo-certo`, equipe `MY_TEAM` (`my-team-6a74`).

## Configuração privada

- `.env`: configuração e credenciais da instalação local; SQLite.
- `.env.production.local`: URIs Transaction/Session pooler, senha separada e chave Django de produção.
- `scripts/production.py` substitui o placeholder da senha com codificação de URL, exige conexões do mesmo projeto e aplica flags de produção somente ao subprocesso.
- Runtime Vercel: `DATABASE_URL` e `DJANGO_SECRET_KEY` como secrets; `DJANGO_DEBUG=0`, cookies seguros e HTTPS habilitados.
- Senha separada e URI de migrations não são necessárias no runtime.
- `.env*`, `.local`, `.vercel`, PDFs, bancos e dependências locais são excluídos do envio. O script de build permanece incluído.

## Banco

Usar `scripts/production.py plan`, `migrate`, `seed` e `privacy`, nessa ordem. Comandos completos em [COMANDOS](../COMANDOS.md).

Migrations e importação são explícitas; não rodam durante build ou requisições. O banco local não é sincronizado automaticamente com produção. Cópia de conta/histórico exige autorização e conferência das revisões das questões; a cópia inicial autorizada preservou conta, meta e duas respostas.

## Deploy

CLI oficial usada: Vercel 64.2.0, instalada em `.local/vercel-cli`; autenticação privada em `.local/vercel-auth`. Em outra máquina, instalar a CLI e fazer login próprio, sem copiar tokens.

1. Confirmar o vínculo com `project inspect`, usando equipe e projeto explícitos.
2. Conferir o pacote com `deploy --dry --json`; não deve incluir credenciais, bancos ou PDFs.
3. Usar `deploy --prod --skip-domain` para construir uma versão de produção para validação.
4. Conferir estado READY, health JSON, assets e tela de entrada. Em URLs protegidas, usar autenticação própria da Vercel, sem desativar a proteção para testes.
5. Promover a versão validada com `promote <URL-ou-ID>` e conferir novamente o domínio público.

O build usa Python 3.12, Node 24, dependências de `requirements.txt` e lockfile npm. Pacotes Python são explicitamente limitados a `config`, `study` e `content`; React é compilado pelo script e os estáticos são coletados pela integração Django da Vercel.
O pacote Python inclui `content/expansion.csv`; conferir esse arquivo no wheel após mudanças no catálogo.

O deploy atual foi enviado pela CLI. Não há publicação automática por Git configurada. Para reverter código, promover um deploy anterior compatível; isso não reverte migrations ou dados.

## Custo do catálogo

Em 16/10/2026, após importar 300 questões, o banco ocupava aproximadamente 12,8 MiB.
O [plano gratuito do Supabase](https://supabase.com/pricing) inclui 500 MB de banco;
essa expansão não exige plano pago. Histórico, acessos e demais recursos seguem sujeitos
às cotas. Projetos gratuitos podem pausar após uma semana de inatividade.

## Backup

Local: `scripts/backup_database.py` gera snapshot SQLite consistente em `.local/backups`, sem parar o servidor.

Supabase: após instalar `pg_dump` compatível, usar `scripts/production.py backup`. A conexão de sessão e TLS são usados sem senha nos argumentos. O dump fica em `.local/backups`; falhas preservam o arquivo parcial e não são reportadas como sucesso.

O backup PostgreSQL e sua restauração ainda precisam de validação. Armazenar cópia protegida fora deste computador e conferir restauração em banco separado antes de depender dela. Não executar testes destrutivos ou restauração sobre produção.
