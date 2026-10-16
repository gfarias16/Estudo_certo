from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from study.database_security import harden


class Command(BaseCommand):
    help = "Revoga acesso de anon/authenticated às tabelas Django; executar após novas migrations no Supabase."

    def handle(self, **options):
        if connection.vendor != "postgresql":
            raise CommandError("Comando exclusivo para PostgreSQL.")
        count = harden(connection)
        self.stdout.write(self.style.SUCCESS(f"{count} tabelas Django verificadas para revogação de acesso da Data API."))
