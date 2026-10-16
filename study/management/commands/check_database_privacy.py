from django.core.management.base import BaseCommand
from django.db import connection

from study.database_security import check_privacy


class Command(BaseCommand):
    help = "Verifica se as funções da Data API do Supabase possuem privilégios nas tabelas Django."

    def handle(self, **options):
        if check_privacy(connection):
            self.stdout.write(self.style.SUCCESS("Sem acesso das funções anon/authenticated às tabelas Django."))
        else:
            self.stdout.write(self.style.WARNING("Funções anon/authenticated ausentes; este PostgreSQL não reproduz as permissões do Supabase."))
