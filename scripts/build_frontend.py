"""Build reproduzível, sem migrations nem importação de dados em produção."""
import os
import shutil
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
if not npm:
    raise SystemExit("Node.js/npm não encontrado no ambiente de build.")
for args in (["ci"], ["run", "build"]):
    subprocess.run([npm, *args], cwd=root / "frontend", check=True)
