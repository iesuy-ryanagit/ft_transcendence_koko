from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Tournament, Match, Score
from .serializers import TournamentSerializer, ScoreSerializer
from .services import create_tournament_schedule, record_score

# Create your views here.
class CreateTournamenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TournamentSerializer(data=request.data)
        if serializer.is_valid():
            tournament = serializer.save()
            create_tournament_schedule(tournament)
            return Response({"message": "Tournament created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RecordScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ScoreSerializer(data=request.data)
        if serializer.is_valid():
            score = serializer.save()
            return Response({"message": "Score recorded successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)