from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    match_history = models.JSONField(default=list, blank=True)
    secret_key = models.CharField(max_length=255, null=True, blank=True)
    otp_enabled = models.BooleanField(default=False)
    def __str__(self):
        return self.username

# class MatchResult(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='match_results')
#     match_date = models.DateTimeField(auto_now_add=True)
#     result = models.CharField(max_length=20)  # 勝利、敗北、引き分けなど
#     score = models.CharField(max_length=20)  # 例: "10-5"

#     def __str__(self):
#         return f"{self.user.username} - {self.match_date} - {self.result}"


