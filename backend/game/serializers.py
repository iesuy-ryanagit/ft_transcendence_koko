from rest_framework import serializers
from .models import GameSetting

class GameSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSetting
        fields = '__all__'
        read_only_fields = ['id', 'user']


class GameSettingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSetting
        fields = ['ball_speed', 'ball_multiplier_enabled', 'score_board', 'timer']