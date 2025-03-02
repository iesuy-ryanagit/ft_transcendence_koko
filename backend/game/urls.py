from django.urls import path
from .views import GameSettingView

urlpatterns = [
    path('game/setting/', GameSettingView.as_view(), name='game_setting'),
]