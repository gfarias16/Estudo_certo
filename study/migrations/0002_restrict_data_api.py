from django.db import migrations


def restrict_data_api(apps, schema_editor):
    from study.database_security import harden

    harden(schema_editor.connection)


class Migration(migrations.Migration):
    dependencies = [
        ("study", "0001_initial"),
        ("sessions", "0001_initial"),
        ("admin", "0003_logentry_add_action_flag_choices"),
    ]
    operations = [
        migrations.RunPython(restrict_data_api, migrations.RunPython.noop),
    ]
