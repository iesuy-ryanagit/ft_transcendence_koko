# Generated by Django 5.1.6 on 2025-02-23 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_remove_customuser_avatar_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='match_history',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='customuser',
            name='secret_key',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
