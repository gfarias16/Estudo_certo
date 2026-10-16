# GitHub e continuidade

Repositório público: https://github.com/gfarias16/Estudo_certo.

## GitHub Desktop

Neste computador, use **File → Add local repository** e selecione
`C:\Users\gabri\Documents\GitHub\Estudo_certo`. A pasta atual é o repositório;
não clone novamente dentro dela.

Em outro computador, clone pelo GitHub Desktop e siga o README. Crie seu próprio
`.env`; não copie autenticação da Vercel. SQLite local e Supabase são independentes.

## Arquivos excluídos

- `.env`, `.env.local`, `.env.production.local` e demais `.env.*`; somente `.env.example` entra no Git.
- `.local/`: bancos, backups, imagens de conferência, extrações, sessões e autenticação da CLI.
- `.vercel/`, `.aws/`, `.codex/` e `.agents/`: configurações locais e credenciais de ferramentas.
- PDFs originais em `docs/`: preservados localmente, sem redistribuição pública.
- `.venv/`, `node_modules/`, builds, estáticos coletados, caches e relatórios de testes.
- Bancos SQLite, dumps, logs, certificados e chaves privadas pelas extensões do `.gitignore`.

O `.gitignore` não remove arquivos já rastreados. Antes de cada publicação, selecione
os caminhos explicitamente, confira `git diff --cached --name-only` e execute:

```powershell
.\.venv\Scripts\python.exe scripts/audit_publication.py
```

A auditoria lê os arquivos preparados no índice, procura credenciais locais conhecidas
e padrões sensíveis sem mostrar seus valores. Não substitui a revisão humana.
Os lockfiles e o catálogo conferido são versionados. A CI usa banco isolado, sem secrets de produção.

O deploy continua pela CLI da Vercel; publicar código no GitHub não configura deploy automático.
