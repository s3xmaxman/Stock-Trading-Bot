# Generated by Django 5.1.3 on 2024-12-01 20:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("market", "0004_rename_compony_stockquote_company"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="stockquote",
            unique_together={("company", "time")},
        ),
    ]