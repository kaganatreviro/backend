# Generated by Django 4.2 on 2024-05-15 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("beverage", "0012_alter_beverage_price"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="beverage",
            index=models.Index(fields=["name"], name="beverage_be_name_57c27e_idx"),
        ),
        migrations.AddIndex(
            model_name="beverage",
            index=models.Index(
                fields=["availability_status"], name="beverage_be_availab_62fdb9_idx"
            ),
        ),
    ]
