from tournament.models import Tournament, Match
from django.contrib.auth import get_user_model
import random

User = get_user_model()

def create_tournament_schedule(tournament: Tournament):
	"""Aoutmatically first schedule of Tournament"""
	participants = list(tournament..all())
	random.shuffle(participants)

	matches = []
	num_matches = len(participants) // 2

	for i in range(num_matches):
		player1 = participants[i * 2]
		player2 = participants[i * 2 + 1]
		match = Match.objects.create(
			tournament=tournament,
			round=1,
			player1=player1,
			player2=player2
		)
		matches.append(match)
	
	tournament.status = "ongoing"
	tournament.save()

def	process_match_result(match: Match, winner: User, score: str):
	"""Record winner of the match, Generate next round match"""
	match.winner = winner
	match.score = score
