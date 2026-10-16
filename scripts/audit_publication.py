"""Audita o índice Git antes de commit/push; nunca imprime valores sensíveis."""
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN_DIRECTORIES = (
    ".local/", ".vercel/", ".venv/", ".aws/", ".codex/", ".agents/",
    "staticfiles/", "build/", "frontend/node_modules/", "frontend/dist/",
    "frontend/test-results/", "frontend/playwright-report/",
)
FORBIDDEN_EXTENSIONS = {".pdf", ".sqlite3", ".sqlite", ".db", ".dump", ".pem", ".key", ".pfx", ".log", ".pyc"}
TOKEN_PATTERNS = (
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"postgres(?:ql)?://[^\s/]+:[^\s@]+@"),
)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def local_secrets():
    values = set()
    for name in (".env", ".env.local", ".env.production.local"):
        path = ROOT / name
        if not path.is_file():
            continue
        fields = dotenv_values(path)
        for key, value in fields.items():
            if value and len(value) >= 8 and any(word in key for word in ("PASSWORD", "SECRET", "TOKEN", "DATABASE_URL", "API_KEY")):
                values.add(value)
                values.add(quote(value, safe=""))
        if fields.get("SUPABASE_DB_PASSWORD"):
            for key in ("DATABASE_URL", "MIGRATION_DATABASE_URL"):
                if fields.get(key):
                    values.add(fields[key].replace("[YOUR-PASSWORD]", quote(fields["SUPABASE_DB_PASSWORD"], safe="")))
    auth = ROOT / ".local" / "vercel-auth" / "auth.json"
    if auth.is_file():
        data = json.loads(auth.read_text(encoding="utf-8"))
        values.update(data[key] for key in ("token", "refreshToken") if data.get(key))
    return values


def main():
    files = [name for name in git("ls-files", "-z").decode("utf-8").split("\0") if name]
    if not files:
        raise SystemExit("Índice Git vazio: selecione explicitamente os arquivos antes da auditoria.")
    secrets = local_secrets()
    findings = []
    for name in files:
        path = Path(name)
        if (name.startswith(FORBIDDEN_DIRECTORIES) or "__pycache__" in path.parts
            or path.suffix.lower() in FORBIDDEN_EXTENSIONS
            or (path.name.startswith(".env") and name != ".env.example")):
            findings.append((name, "arquivo local ou sensível no índice"))
            continue
        data = git("show", ":" + name).decode("utf-8", errors="replace")
        if any(secret in data for secret in secrets):
            findings.append((name, "coincidência com credencial local"))
        if any(pattern.search(data) for pattern in TOKEN_PATTERNS):
            findings.append((name, "padrão de token, chave privada ou URI com senha"))
    for name, reason in findings:
        print(f"BLOQUEADO: {name}: {reason}")
    if findings:
        return 1
    print(f"Auditoria aprovada: {len(files)} arquivos no índice; nenhum segredo conhecido ou padrão sensível detectado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
