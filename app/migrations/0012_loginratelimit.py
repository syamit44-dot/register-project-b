from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0011_weight_scale_app_users"),
    ]

    operations = [
        migrations.CreateModel(
            name="LoginRateLimit",
            fields=[
                ("key", models.CharField(max_length=64, primary_key=True, serialize=False)),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("window_started_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={"db_table": "login_rate_limit"},
        ),
    ]
