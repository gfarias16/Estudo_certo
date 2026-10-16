"""Cria apenas funções de teste para reproduzir a fronteira da Data API na CI."""
import os
from urllib.parse import urlparse

import psycopg

url = os.environ.get("DATABASE_URL", "")
parsed = urlparse(url)
if os.environ.get("CI") != "true" or parsed.hostname != "127.0.0.1" or parsed.path != "/study_ci":
    raise SystemExit("Permitido somente na base PostgreSQL efêmera da CI.")
with psycopg.connect(url, autocommit=True) as connection:
    for role in ("anon", "authenticated"):
        exists = connection.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [role]).fetchone()
        if not exists:
            connection.execute(psycopg.sql.SQL("CREATE ROLE {} NOLOGIN").format(psycopg.sql.Identifier(role)))
print("Funções de teste da Data API preparadas.")
