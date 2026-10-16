"""Prepara apenas SQLite local e uma conta inicial, sem imprimir credenciais."""
import os
import secrets
import shutil
import sys
from pathlib import Path

from dotenv import dotenv_values, set_key

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
env_path = root / ".env"
values = dotenv_values(env_path) if env_path.exists() else {}
if values.get("DATABASE_URL") or os.getenv("DATABASE_URL"):
    raise SystemExit("Preparação local recusada: DATABASE_URL já configurada. Nenhum banco remoto foi alterado.")
if not env_path.exists():
    shutil.copyfile(root / ".env.example", env_path)
if not values.get("DJANGO_SECRET_KEY"):
    set_key(str(env_path), "DJANGO_SECRET_KEY", secrets.token_urlsafe(64))
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
os.environ["DJANGO_DEBUG"] = "1"
os.environ["DJANGO_LOCAL_DATABASE"] = "db.sqlite3"
os.environ["MIGRATION_DATABASE_URL"] = ""
import django  # noqa: E402

django.setup()
from django.contrib.auth import get_user_model  # noqa: E402
from django.core.management import call_command  # noqa: E402

call_command("migrate", verbosity=0)
call_command("import_catalog", verify_sources=True)
username = "estudante"
if not get_user_model().objects.filter(username=username).exists():
    password = secrets.token_urlsafe(20)
    get_user_model().objects.create_user(username=username, password=password, first_name="Estudante")
    set_key(str(env_path), "LOCAL_STUDENT_USERNAME", username)
    set_key(str(env_path), "LOCAL_STUDENT_PASSWORD", password)
    print("Conta local criada. Usuário e senha estão somente no .env, nas chaves LOCAL_STUDENT_*.")
else:
    print("Conta local existente preservada; a senha não foi alterada.")
print("SQLite local preparado. Nenhum banco remoto foi acessado.")
