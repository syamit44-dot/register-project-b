from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("app", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="profileuser",
            name="login_username",
            field=models.CharField(
                blank=True, editable=False, max_length=50, null=True, unique=True
            ),
        ),
    ]
