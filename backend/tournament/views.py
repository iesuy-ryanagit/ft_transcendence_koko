from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from .models import Tournament
from .serializers import (
    TournamentSerializer,
    TournamentJoinSerializer,
    MatchEndSerializer,
    TournamentListSerializer,
    TournamentDetailSerializer,
    TournamentParticipantSerializer,
    TournamentFinishSerializer,
    TournamentStartSerializer,
    MatchDetailSerializer
)
from .services import create_tournament_schedule, process_match_result, start_tournament

# Create your views here.
class CreateTournamenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TournamentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            tournament = serializer.save()
            create_tournament_schedule(tournament)

            response_serializer = TournamentSerializer(tournament)
            return Response(
                {
                    "message": "Tournament created successfully",
                    "tournament": response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JoinTournamentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TournamentJoinSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            tournament = serializer.save()
            return Response(
                {"message": "Joined tournament successfully", "tournament_id": str(tournament.id)},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class JoinTournamentParticipantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TournamentParticipantSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            participant = serializer.save()
            tournament = participant.tournament

            if tournament.tournament_participants.count() >= tournament.max_participants:
                create_tournament_schedule(tournament)
            return Response(
                {
                    "message": "Joined tournament participant successfully",
                    "participant_id": str(participant.id),
                    "alias": participant.alias
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MatchEndView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MatchEndSerializer(data=request.data)
        if serializer.is_valid():
            match = serializer.save()
            result = process_match_result(match, match.winner, match.final_score)
            return Response({
                "message": "Match result recorded successfully",
                "match_id": str(match.id),
                "final_score": match.score,
                "winner": match.winner.id if match.winner else None,
                "next_round": result
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TournamentListView(generics.ListAPIView):
    """List all tournaments"""
    queryset = Tournament.objects.all().order_by('-created_at')
    serializer_class = TournamentListSerializer

class TournamentDetailView(generics.RetrieveAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentDetailSerializer

class TournamentFinishView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TournamentFinishSerializer(data=request.data)
        if serializer.is_valid():
            tournament = serializer.save()

            response_serializer = TournamentDetailSerializer(tournament)
            return Response(
                {
                    "message": "Tournament finished successfully", 
                    "tournament": response_serializer.data
                }, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TournamentStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TournamentStartSerializer(data=request.data)
        if serializer.is_valid():
            tournament_id = serializer.validated_data['tournament_id']
            tournament = Tournament.objects.get(id=tournament_id)

            try:
                matches = start_tournament(tournament)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
            matches_serializer = MatchDetailSerializer(matches, many=True)
            return Response(
                {
                    "message": "Tournament started successfully",
                    "matches": matches_serializer.data
                }, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)