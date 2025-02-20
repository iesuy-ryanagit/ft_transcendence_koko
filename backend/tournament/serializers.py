from rest_framework import serializers
from tournament.models import Tournament, Match, TournamentParticipant
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class TournamentSerializer(serializers.ModelSerializer):
    # auto_join is a boolean field that is to join the tournament automatically when created
    auto_join = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'max_participants', 'auto_join']

    def create(self, validated_data):
        # To take out auto_join from the validated data
        auto_join = validated_data.pop('auto_join', False)
        #Create tournament instance
        tournament = Tournament.objects.create(**validated_data)

        # If auto_join is true and the user is authenticated, add the user to the tournament
        # request = self.context.get('request')
        # if request and auto_join and request.user.is_authenticated:
        #     TournamentParticipant.objects.create(
        #         tournament=tournament,
        #         user=request.user,
        #         alias=request.user.username
        #     )

        return tournament
    
class TournamentParticipantSerializer(serializers.ModelSerializer):
    tournament_id = serializers.UUIDField(write_only=True)
    alias = serializers.CharField(max_length=100)

    class Meta:
        model = TournamentParticipant
        fields = ['tournament_id', 'alias']

    def validate(self, data):
        tournament_id = data.get('tournament_id')
        alias = data.get('alias')

        try:
            tournament = Tournament.objects.get(id=tournament_id)
        except Tournament.DoesNotExist:
            raise serializers.ValidationError("Tournament does not exist")
        
        if tournament.tournament_participants.count() >= tournament.max_participants:
            raise serializers.ValidationError("Tournament is full")
        
        if TournamentParticipant.objects.filter(tournament=tournament, alias=alias).exists():
            raise serializers.ValidationError("Alias already exists")
        
        # request = self.context.get('request')
        # if request and TournamentParticipant.objects.filter(tournament=tournament, user=request.user).exists():
        #     raise serializers.ValidationError("You are already in this tournament")
        
        data['tournament'] = tournament
        return data
    
    def create(self, validated_data):
        tournament = validated_data.pop('tournament')
        alias = validated_data.pop('alias')
        request = self.context.get('request')
        user = request.user if request else None

        participant = TournamentParticipant.objects.create(
            tournament=tournament,
            user=user,
            alias=alias
        )
        return participant
    
class TournamentJoinSerializer(serializers.Serializer):
    tournament_id = serializers.UUIDField()

    def validate_tournament_id(self, value):
        try:
            tournament = Tournament.objects.get(id=value)
        except Tournament.DoesNotExist:
            raise serializers.ValidationError("Tournament does not exist")
        
        # Check if the tournament is full
        if tournament.tournament_participants.count() >= tournament.max_participants:
            raise serializers.ValidationError("Tournament is full")
        
        return value
    
    def create(self, validated_data):
        tournament = Tournament.objects.get(id=validated_data['tournament_id'])
        request = self.context.get('request')
        user = request.user if request else None

        if TournamentParticipant.objects.filter(tournament=tournament, user=user).exists():
            raise serializers.ValidationError("You are already in this tournament")
        
        TournamentParticipant.objects.create(
            tournament=tournament,
            user=user,
            alias=user.username
        )
        return tournament
        
class MatchEndSerializer(serializers.Serializer):
    match_id = serializers.UUIDField()
    final_score = serializers.CharField(max_length=10)
    winner = serializers.PrimaryKeyRelatedField(queryset=TournamentParticipant.objects.all())

    def validate(self, data):
        match_id = data.get('match_id')
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            raise serializers.ValidationError("Match does not exist")
        if match.status == "completed":
            raise serializers.ValidationError("Match already completed")
        
        winner = data.get('winner')
        if winner not in [match.player1, match.player2]:
            raise serializers.ValidationError("Winner is not a participant in this match")
        data['match'] = match
        return data

    def create(self, validated_data):
        match_id = validated_data.get("match_id")
        final_score = validated_data.get("final_score")
        winner = validated_data.get("winner")

        match = Match.objects.get(id=match_id)
        match.status = "completed"
        match.final_score = final_score
        match.winner = winner
        match.end_time = timezone.now()
        match.save()

        # call out to process_match_result when it is needed
        # process_match_result(match, winner, final_score)

        return match
        

class TournamentListSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Tournament
        fields = '__all__'

class TournamentParticipantDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentParticipant
        fields = ['id', 'alias', 'user']

class MatchDetailSerializer(serializers.ModelSerializer):
    player1 = TournamentParticipantDetailSerializer(read_only=True)
    player2 = TournamentParticipantDetailSerializer(read_only=True)
    winner = TournamentParticipantDetailSerializer(read_only=True)
    tournament = serializers.StringRelatedField()

    class Meta:
        model = Match
        fields = '__all__'

class TournamentDetailSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    matches = MatchDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Tournament
        fields = '__all__'

class TournamentFinishSerializer(serializers.Serializer):
    tournament_id = serializers.UUIDField()

    def validate_tournament_id(self, value):
        try:
            tournament = Tournament.objects.get(id=value)
        except Tournament.DoesNotExist:
            raise serializers.ValidationError("Tournament does not exist")

        incomplete_matches = tournament.matches.filter(status__in=["pending", "ongoing"])
        if incomplete_matches.exists():
            raise serializers.ValidationError("Not all matches are completed.")
        return value

    def create(self, validated_data):
        tournament = Tournament.objects.get(id=validated_data['tournament_id'])

        final_match = tournament.matches.filter(status="completed").order_by('end_time').last()
        if not final_match or not final_match.winner:
            raise serializers.ValidationError("Final match winner could not be determined.")
        
        tournament.winner = final_match.winner
        tournament.status = "completed"
        tournament.save()
        return tournament

class TournamentStartSerializer(serializers.Serializer):
    tournament_id = serializers.UUIDField()

    def validate_tournament_id(self, value):
        try:
            tournament = Tournament.objects.get(id=value)
        except Tournament.DoesNotExist:
            raise serializers.ValidationError("Tournament does not exist")
        if tournament.status != "pending":
            raise serializers.ValidationError("Tournament is not pending")
        return value
    
    