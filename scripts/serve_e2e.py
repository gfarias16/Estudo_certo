"""Servidor de teste com banco separado. Não altera o histórico do estudante."""
import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if not (root / "frontend" / "dist" / "index.html").exists():
    raise SystemExit("Execute npm run build no frontend antes dos testes E2E.")
sys.path.insert(0, str(root))
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
os.environ["DJANGO_DEBUG"] = "1"
os.environ["DJANGO_LOCAL_DATABASE"] = "e2e.sqlite3"
os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"] = "http://127.0.0.1:5173,http://localhost:5173"
os.environ["DATABASE_URL"] = ""
os.environ["MIGRATION_DATABASE_URL"] = ""
os.environ["DJANGO_FORCE_HTTPS"] = "0"
os.environ["DJANGO_SECURE_COOKIES"] = "0"
if not os.environ.get("E2E_PASSWORD"):
    raise SystemExit("E2E_PASSWORD deve ser gerada pelo executor de testes.")

import django  # noqa: E402

django.setup()
from django.contrib.auth import get_user_model  # noqa: E402
from django.core.management import call_command  # noqa: E402

from study.models import Attempt, LoginWindow, StudyProfile  # noqa: E402

call_command("migrate", verbosity=0)
call_command("import_catalog", verbosity=0)
user, _ = get_user_model().objects.get_or_create(username="estudante-e2e")
user.set_password(os.environ["E2E_PASSWORD"])
user.first_name = "Estudante"
user.save()
Attempt.objects.filter(user=user).delete()
LoginWindow.objects.all().delete()
StudyProfile.objects.filter(user=user).delete()
subprocess.run([sys.executable, str(root / "manage.py"), "runserver", "127.0.0.1:8001", "--noreload"], check=True)
