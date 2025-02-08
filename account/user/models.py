from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    otp_enabled = models.BooleanField(default=False)
    default_language = models.CharField(
        max_length=10,
        default="en", 
        help_text="The user's preferred default language.",
    )

    def __str__(self):
        return self.username
