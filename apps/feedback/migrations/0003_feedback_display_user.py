# Generated by Django 4.2 on 2024-05-21 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("feedback", "0002_feedbackanswer_display_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="feedback",
            name="display_user",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
