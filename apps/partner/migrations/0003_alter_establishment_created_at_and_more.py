# Generated by Django 4.2 on 2024-04-19 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("partner", "0002_remove_establishment_location_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="establishment",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="establishment",
            name="modified_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
