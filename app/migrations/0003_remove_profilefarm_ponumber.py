from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("app", "0002_profileuser_login_username")]

    operations = [
        migrations.RemoveField(model_name="profilefarm", name="poNumber"),
    ]
