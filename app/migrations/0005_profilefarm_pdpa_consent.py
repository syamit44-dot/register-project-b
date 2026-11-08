from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("app", "0004_profilefarm_icon_id")]

    operations = [
        migrations.AddField(
            model_name="profilefarm",
            name="pdpa_consent",
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]
