from getpass import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Cria uma conta de estudo sem expor senha no terminal, argumentos ou arquivos."

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("--name", default="")
        parser.add_argument("--admin", action="store_true", help="Concede acesso administrativo; omita para conta de estudante.")

    @transaction.atomic
    def handle(self, username, **options):
        user_model = get_user_model()
        if user_model.objects.filter(username=username).exists():
            raise CommandError("Usuário já existe. Para redefinir senha, utilize changepassword.")
        user = user_model(username=username, first_name=options["name"])
        try:
            user.full_clean(exclude=["password"])
        except ValidationError as exc:
            raise CommandError(" ".join(exc.messages)) from exc
        password = getpass("Senha (não será exibida): ")
        if password != getpass("Confirme a senha: "):
            raise CommandError("As senhas não coincidem.")
        try:
            validate_password(password, user)
        except ValidationError as exc:
            raise CommandError(" ".join(exc.messages)) from exc
        user.set_password(password)
        user.is_staff = options["admin"]
        user.is_superuser = options["admin"]
        user.save()
        self.stdout.write(self.style.SUCCESS("Conta criada. A senha não foi registrada em arquivos ou logs."))
