from django.db import migrations, models
from django.db.models.functions import Lower


class Migration(migrations.Migration):
    dependencies = [("app", "0008_distributor_and_seller_labels")]

    operations = [
        # The output field already defines the database column as varchar(50).
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name="profileuser",
                    name="login_username_key",
                    field=models.GeneratedField(
                        expression=Lower("login_username"),
                        output_field=models.CharField(max_length=50),
                        max_length=50,
                        db_persist=False,
                        null=True,
                        unique=True,
                    ),
                ),
            ],
        ),
    ]
