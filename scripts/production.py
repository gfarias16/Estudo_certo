"""Executa operações explícitas de publicação sem alterar o ambiente local."""
import argparse
import os
import secrets
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, urlsplit

from dotenv import dotenv_values, set_key

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env.production.local"
COMMANDS = {
    "backup": None,
    "plan": ["migrate", "--plan"],
    "migrate": ["migrate", "--noinput"],
    "seed": ["import_catalog", "--verify-sources"],
    "privacy": ["check_database_privacy"],
    "harden": ["harden_database"],
    "check": ["check", "--deploy"],
}


def production_environment():
    values = dotenv_values(ENV_FILE)
    password = values.get("SUPABASE_DB_PASSWORD") or ""
    result = {}
    endpoints = []
    for key, port in (("DATABASE_URL", 6543), ("MIGRATION_DATABASE_URL", 5432)):
        raw = (values.get(key) or "").strip()
        if "[YOUR-PASSWORD]" in raw and not password:
            raise ValueError("Preencha SUPABASE_DB_PASSWORD no arquivo privado de publicação.")
        resolved = raw.replace("[YOUR-PASSWORD]", quote(password, safe=""))
        parsed = urlsplit(resolved)
        if (
            parsed.scheme not in {"postgres", "postgresql"}
            or not (parsed.hostname or "").endswith(".pooler.supabase.com")
            or parsed.port != port
            or not parsed.password
            or not parsed.username
            or parsed.path != "/postgres"
        ):
            raise ValueError(f"Confira a URI e o modo de conexão em {key}.")
        endpoints.append((parsed.hostname, parsed.username))
        result[key] = resolved
    if endpoints[0] != endpoints[1]:
        raise ValueError("As duas conexões devem pertencer ao mesmo projeto Supabase.")
    secret = values.get("DJANGO_SECRET_KEY")
    if not secret:
        secret = secrets.token_urlsafe(64)
        set_key(str(ENV_FILE), "DJANGO_SECRET_KEY", secret)
    result.update({
        "DJANGO_SECRET_KEY": secret,
        "DJANGO_DEBUG": "0",
        "DJANGO_SECURE_COOKIES": "1",
        "DJANGO_FORCE_HTTPS": "1",
        "DJANGO_ALLOWED_HOSTS": values.get("DJANGO_ALLOWED_HOSTS") or "localhost,127.0.0.1",
        "DJANGO_CSRF_TRUSTED_ORIGINS": values.get("DJANGO_CSRF_TRUSTED_ORIGINS") or "",
    })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=COMMANDS)
    args = parser.parse_args()
    try:
        production = production_environment()
    except ValueError:
        parser.exit(1, "Configuração privada inválida. Confira as URIs, portas e senha, sem publicá-las.\n")
    env = {**os.environ, **production}
    if args.operation in {"plan", "migrate", "seed", "harden"}:
        env["DATABASE_URL"] = production["MIGRATION_DATABASE_URL"]
    command = (
        [sys.executable, str(ROOT / "scripts" / "backup_database.py")]
        if args.operation == "backup"
        else [sys.executable, str(ROOT / "manage.py"), *COMMANDS[args.operation]]
    )
    process = subprocess.run(
        command,
        cwd=ROOT, env=env, capture_output=True, text=True, check=False,
    )
    # Bibliotecas podem inserir dados de conexão em exceções; sanitize antes de mostrar.
    output = process.stdout + process.stderr
    for value in (production["DATABASE_URL"], production["MIGRATION_DATABASE_URL"],
                  dotenv_values(ENV_FILE).get("SUPABASE_DB_PASSWORD")):
        if value:
            output = output.replace(value, "[credencial omitida]")
    sys.stdout.write(output)
    return process.returncode


if __name__ == "__main__":
    raise SystemExit(main())
