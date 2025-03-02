# Generated by Django 4.2.19 on 2025-02-17 14:12

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tournament', '0004_match_winner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='participants',
            field=models.ManyToManyField(blank=True, related_name='tournaments', to=settings.AUTH_USER_MODEL),
        ),
    ]
