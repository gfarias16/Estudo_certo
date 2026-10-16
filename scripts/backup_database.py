"""Backup consistente do banco configurado. Não imprime credenciais ou conteúdo."""
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from dotenv import load_dotenv

root = Path(__file__).resolve().parent.parent
load_dotenv(root / ".env")
destination = root / ".local" / "backups"
destination.mkdir(parents=True, exist_ok=True)
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
url = os.getenv("MIGRATION_DATABASE_URL") or os.getenv("DATABASE_URL")
if not url:
    source = root / ".local" / os.getenv("DJANGO_LOCAL_DATABASE", "db.sqlite3")
    if not source.is_file():
        raise SystemExit("Banco local não encontrado; nenhum backup foi criado.")
    target = destination / f"estudo-certo-{stamp}.sqlite3"
    with sqlite3.connect(f"file:{source.as_posix()}?mode=ro", uri=True) as source_db:
        with sqlite3.connect(target) as backup_db:
            source_db.backup(backup_db)
else:
    pg_dump = shutil.which("pg_dump")
    if not pg_dump:
        raise SystemExit("Instale o cliente PostgreSQL com pg_dump antes de criar o backup remoto.")
    parsed = urlparse(url)
    if parsed.scheme not in {"postgres", "postgresql"}:
        raise SystemExit("O backup remoto exige uma URL PostgreSQL.")
    env = dict(os.environ)
    env.update({
        "PGHOST": parsed.hostname or "",
        "PGPORT": str(parsed.port or 5432),
        "PGUSER": unquote(parsed.username or ""),
        "PGPASSWORD": unquote(parsed.password or ""),
        "PGDATABASE": unquote(parsed.path.lstrip("/")),
        "PGSSLMODE": parse_qs(parsed.query).get("sslmode", ["require"])[0],
    })
    partial = destination / f"estudo-certo-{stamp}.dump.partial"
    result = subprocess.run(
        [pg_dump, "--format=custom", "--no-owner", "--no-acl", f"--file={partial}"],
        env=env, capture_output=True, check=False,
    )
    if result.returncode:
        raise SystemExit(f"Backup PostgreSQL falhou (código {result.returncode}). Confira acesso, versão do pg_dump e conexão direta/session pooler; arquivo parcial preservado.")
    target = partial.with_suffix("")
    partial.rename(target)
sys.stdout.write(f"Backup concluído: {target.relative_to(root)}\n")
