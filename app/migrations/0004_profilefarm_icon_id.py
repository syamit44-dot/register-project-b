from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("app", "0003_remove_profilefarm_ponumber")]

    operations = [
        migrations.AddField(
            model_name="profilefarm",
            name="icon_id",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "Barn"), (1, "Egg"), (2, "Leaf")], default=0
            ),
        ),
        migrations.AddConstraint(
            model_name="profilefarm",
            constraint=models.CheckConstraint(
                condition=models.Q(icon_id__in=[0, 1, 2]), name="valid_farm_icon_id"
            ),
        ),
    ]
