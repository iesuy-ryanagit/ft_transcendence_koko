from tournament.models import Tournament, Match, TournamentParticipant
from django.contrib.auth import get_user_model
from django.utils import timezone
import random

User = get_user_model()

def create_tournament_schedule(tournament: Tournament):
	"""Aoutmatically first schedule of Tournament"""
	print(f"Creating schedule for {tournament.name}")
	participants_qs = TournamentParticipant.objects.filter(tournament=tournament)
	participants = [tp.user for tp in participants_qs]
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
	
	tournament.status = "pending"
	tournament.save()

	return matches

def	process_match_result(match: Match, winner: User, score: str): # type: ignore
	"""Record winner of the match, Generate next round match"""
	match.winner = winner
	match.final_score = score
	match.status = "completed"
	match.end_time = timezone.now()
	match.save()

	tournament = match.tournament
	current_round = match.round

	#2. Check if there are remaining matches in the current round
	remaining_matches = Match.objects.filter(
		tournament=tournament,
		round=current_round,
		status="pending"
	)
	if remaining_matches.exists():
		return "Next round pending"
	
	#3. ALL matches in the current round are completed
	# Retrieve the matches in the order they were created
	round_matches = Match.objects.filter(
		tournament=tournament,
		round=current_round
	).order_by('id')


	# Collect the winners of each match
	winners = [m.winner for m in round_matches]

	# If only winner is present, the tournament is over.
	if len(winners) == 1:
		tournament.winner = winners[0].user
		tournament.status = "completed"
		tournament.current_round = current_round
		tournament.save()
		return "Tournament completed"
	
	#4. Create matches for the next round
	new_round = current_round + 1
	new_matches = []

	for i  in range(0, len(winners), 2):
		if i + 1 < len(winners):
			new_match = Match.objects.create(
				tournament=tournament,
				round=new_round,
				player1=winners[i],
				player2=winners[i + 1], 
				status="pending"
			)
			new_matches.append(new_match)

	tournament.current_round = new_round
	tournament.save()

	return new_matches


def start_tournament(tournament: Tournament):

	# participants_qs = TournamentParticipant.objects.filter(tournament=tournament)
	# participants = [tp.user for tp in participants_qs]

	participants = list(tournament.tournament_participants.all())
	# num_participants = len(participants)
	# if num_participants < 2:
	# 	raise Exception("Not enough participants to start tournament.")
	# if num_participants % 2 != 0:
	# 	raise Exception("Participants count must be even to start tournament.")
	
	random.shuffle(participants)
	matches = []
	current_round = 1

	for i in range(0, len(participants), 2):
		player1 = participants[i]
		player2 = participants[i + 1]
		match = Match.objects.create(
			tournament=tournament,
			round=current_round,
			player1=player1,
			player2=player2,
			status="pending"
		)
		matches.append(match)
	
	tournament.status = "ongoing"
	tournament.current_round = current_round
	tournament.save()
	return matches
	


# def record_score(match: Match, player: User, score: int):
# 	"""Record score for a match"""
# 	return Score.objects.create(
# 		match=match,
# 		player=player,
# 		score=score
# 	)
	
	