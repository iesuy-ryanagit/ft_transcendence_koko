# Generated by Django 4.2.19 on 2025-03-08 05:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='score',
            name='player',
        ),
        migrations.RemoveField(
            model_name='tournamentparticipant',
            name='user',
        ),
    ]
