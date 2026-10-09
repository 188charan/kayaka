import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PlatformRoleAssignment",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid7, editable=False, primary_key=True, serialize=False)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("PLATFORM_ADMIN", "Platform admin"),
                            ("SUPPORT", "Support"),
                            ("ANALYST", "Analyst"),
                        ],
                        max_length=32,
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="platform_roles",
                        to="accounts.user",
                    ),
                ),
            ],
            options={
                "db_table": "platform_role_assignments",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("user", "role"), name="platform_role_unique_per_user"
                    )
                ],
            },
        ),
    ]
