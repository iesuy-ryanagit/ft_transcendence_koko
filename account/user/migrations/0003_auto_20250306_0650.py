# Generated by Django 3.2.25 on 2025-03-06 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_customuser_otp_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='ball_speed',
            field=models.DecimalField(decimal_places=2, default=1.0, max_digits=5),
        ),
        migrations.AddField(
            model_name='customuser',
            name='timer',
            field=models.PositiveIntegerField(default=60),
        ),
    ]
