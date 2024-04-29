# Generated by Django 4.2 on 2024-04-29 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("beverage", "0009_auto_20240429_2202"),
    ]

    operations = [
        migrations.AlterField(
            model_name="beverage",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="beverages",
                to="beverage.category",
            ),
        ),
    ]