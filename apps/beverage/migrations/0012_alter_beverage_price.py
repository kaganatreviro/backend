# Generated by Django 4.2 on 2024-05-13 21:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("beverage", "0011_alter_beverage_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="beverage",
            name="price",
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]
