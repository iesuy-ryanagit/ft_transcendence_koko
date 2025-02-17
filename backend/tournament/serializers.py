from rest_framework import serializers
from tournament.models import Tournament, Match, Score

class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = '__all__'

class TournamentSerializer(serializers.ModelSerializer):
    scores = ScoreSerializer(many=True, read_only=True)

    class Meta:
        model = Tournament
        fields = '__all__'
