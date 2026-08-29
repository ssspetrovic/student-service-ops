from django.db import migrations


TABLE_NAME = "accounts_user"
COLUMN_NAME = "username"


def column_names(schema_editor):
    with schema_editor.connection.cursor() as cursor:
        return {
            column.name
            for column in schema_editor.connection.introspection.get_table_description(
                cursor, TABLE_NAME
            )
        }


def drop_username_column(apps, schema_editor):
    if schema_editor.connection.vendor == "sqlite":
        return
    if COLUMN_NAME not in column_names(schema_editor):
        return
    table = schema_editor.quote_name(TABLE_NAME)
    column = schema_editor.quote_name(COLUMN_NAME)
    schema_editor.execute(f"ALTER TABLE {table} DROP COLUMN {column}")


class Migration(migrations.Migration):
    """Irreversibly remove the retired username column after image promotion."""

    dependencies = [
        ("accounts", "0005_retire_username_compatibility"),
    ]

    operations = [
        migrations.RunPython(drop_username_column, reverse_code=None),
    ]
