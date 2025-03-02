# Generated by Django 4.2.19 on 2025-02-19 07:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tournament', '0006_rename_score_match_final_score_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tournament',
            name='participants',
        ),
        migrations.CreateModel(
            name='TournamentParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=100)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournament_participants', to='tournament.tournament')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tournament_entries', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('tournament', 'alias')},
            },
        ),
    ]
