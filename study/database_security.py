from django.core.management.base import CommandError


def app_tables(connection):
    return [
        name for name in connection.introspection.table_names()
        if name.startswith(("auth_", "django_", "study_"))
    ]


def data_api_roles(connection):
    with connection.cursor() as cursor:
        cursor.execute("SELECT rolname FROM pg_roles WHERE rolname IN ('anon', 'authenticated')")
        return [row[0] for row in cursor.fetchall()]


def harden(connection):
    if connection.vendor != "postgresql":
        return 0
    roles = data_api_roles(connection)
    tables = app_tables(connection)
    with connection.cursor() as cursor:
        for role in roles:
            for table in tables:
                cursor.execute(
                    f"REVOKE ALL PRIVILEGES ON TABLE {connection.ops.quote_name(table)} "
                    f"FROM {connection.ops.quote_name(role)}"
                )
    return len(tables)


def check_privacy(connection):
    if connection.vendor != "postgresql":
        raise CommandError("Esta verificação exige PostgreSQL. SQLite não valida permissões do Supabase.")
    violations = []
    roles = data_api_roles(connection)
    with connection.cursor() as cursor:
        for role in roles:
            for table in app_tables(connection):
                cursor.execute(
                    "SELECT has_table_privilege(%s, %s, 'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')",
                    [role, connection.ops.quote_name(table)],
                )
                if cursor.fetchone()[0]:
                    violations.append(table)
    if violations:
        raise CommandError("Há tabelas acessíveis às funções da Data API. Execute harden_database e confira os privilégios.")
    return bool(roles)
