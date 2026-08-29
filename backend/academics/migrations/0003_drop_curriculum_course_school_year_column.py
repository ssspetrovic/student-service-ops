from django.db import migrations


TABLE_NAME = "academics_curriculumcourse"
COLUMN_NAME = "school_year"


def column_names(schema_editor):
    with schema_editor.connection.cursor() as cursor:
        return {
            column.name
            for column in schema_editor.connection.introspection.get_table_description(
                cursor, TABLE_NAME
            )
        }


def drop_legacy_school_year(apps, schema_editor):
    if COLUMN_NAME not in column_names(schema_editor):
        return
    table = schema_editor.quote_name(TABLE_NAME)
    column = schema_editor.quote_name(COLUMN_NAME)
    schema_editor.execute(f"ALTER TABLE {table} DROP COLUMN {column}")


class Migration(migrations.Migration):
    """Irreversibly remove the leftover pre-0002 database column if present."""

    dependencies = [
        ("academics", "0002_remove_curriculum_course_school_year"),
    ]

    operations = [
        migrations.RunPython(drop_legacy_school_year, reverse_code=None),
    ]
