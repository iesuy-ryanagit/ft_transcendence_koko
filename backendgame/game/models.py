import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class GameSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="game_settings")

    # 一定
    ball_size = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    paddle_speed = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    paddle_size = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)


    #　可変（ユーザーが設定可能）
    ball_speed = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    ball_num = models.PositiveIntegerField(default=1)

    timer = models.PositiveIntegerField(default=60)
    score_board= models.BooleanField(default=True)

    ball_multiplier_enabled = models.BooleanField(default=False)

    #extra
    background_song = models.CharField(max_length=255, default="default_song.mp3")
    background_image = models.CharField(max_length=255, default="default_image.png")

    def __str__(self):
        return f"GameSetting for {self.user.username}"
