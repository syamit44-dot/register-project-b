from django.db import migrations, models
from django.db.models.functions import Lower


class Migration(migrations.Migration):
    dependencies = [("app", "0005_profilefarm_pdpa_consent")]

    operations = [
        migrations.AddField(
            model_name="profileuser",
            name="login_username_key",
            field=models.GeneratedField(
                expression=Lower("login_username"),
                output_field=models.CharField(max_length=50),
                db_persist=False,
                null=True,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="profileuser",
            name="login_username",
            field=models.CharField(blank=True, editable=False, max_length=50, null=True),
        ),
    ]
