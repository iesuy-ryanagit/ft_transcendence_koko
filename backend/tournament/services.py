from tournament.models import Tournament, Match, Score
from django.contrib.auth import get_user_model
import random

User = get_user_model()

def create_tournament_schedule(tournament: Tournament):
	"""Aoutmatically first schedule of Tournament"""
	print(f"Creating schedule for {tournament.name}")
	participants = list(tournament.participants.all())
	print(f"Participants: {participants}")
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
		print(f"Created match: {match}")
		matches.append(match)
	
	tournament.status = "ongoing"
	tournament.save()

	return matches

def	process_match_result(match: Match, winner: User, score: str):
	"""Record winner of the match, Generate next round match"""
	match.winner = winner
	match.score = score
	match.status = "completed"
	match.save()

	tournament = match.tournament
	current_round = match.round

	remaining_matches = Match.objects.filter(
		tournament=tournament,
		round=current_round,
		status="pending"
	)

	if not remaining_matches.exists():
		winner = Match.objects.filter(
			tournament=tournament,
			round=current_round,
		).values_list('winner', flat=True)

		if len(winner) == 1:
			tournament.winner = User.objects.get(id=winner[0])
			tournament.status = "completed"
			tournament.save()
			return "Tournament completed"
		
		new_matches = []
		for i in range(0, len(winner), 2):
			if i + 1 < len(winner):
				player1 = User.objects.get(id=winner[i])
				player2 = User.objects.get(id=winner[i + 1])
				match = Match.objects.create(
					tournament=tournament,
					round=current_round + 1,
					player1=player1,
					player2=player2
				)
				new_matches.append(match)
		return new_matches
	
	return "Next round pending"

def record_score(match: Match, player: User, score: int):
	"""Record score for a match"""
	return Score.objects.create(
		match=match,
		player=player,
		score=score
	)
	
	