from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    match_history = models.JSONField(default=list, blank=True)
    otp_enabled = models.BooleanField(default=False)
    ball_speed = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    timer = models.PositiveIntegerField(default=60)

    def __str__(self):
        return self.username