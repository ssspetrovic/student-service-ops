from django.db import migrations, models


class Migration(migrations.Migration):
    """Retire username from Django while retaining the database column temporarily."""

    dependencies = [
        ("accounts", "0004_alter_studentprofile_curriculum"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.AlterField(
                    model_name="user",
                    name="username",
                    field=models.CharField(
                        blank=True,
                        editable=False,
                        max_length=150,
                        null=True,
                        unique=True,
                    ),
                ),
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name="user",
                    name="username",
                ),
            ],
        ),
    ]
