import uuid
from django.db import models

# Create your models here.
class Tournament(models.Model):
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('ongoing', 'Ongoing'),
		('completed', 'Completed'),
	]

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=255)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
	created_at = models.DateTimeField(auto_now_add=True)
	max_participants = models.IntegerField()
	winner = models.ForeignKey(
		"TournamentParticipant",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="tournament_wins"
	)
	current_round = models.IntegerField(default=1)
	# participants = models.ManyToManyField(User, related_name='tournaments', blank=True)
	
	def __str__(self):
		return f"{self.name} - {self.status}"

class TournamentParticipant(models.Model):
	# the following id filed are implicitly created by django	
	# id = models.AutoFiled(primary_key=True)
	tournament = models.ForeignKey(Tournament, related_name="tournament_participants", on_delete=models.CASCADE)
	# user = models.ForeignKey(User, related_name="tournament_entries", on_delete=models.CASCADE)
	alias = models.CharField(max_length=100)

	class Meta:
		unique_together = ('tournament', 'alias')

	def __str__(self):
		return f"{self.alias}in {self.tournament.name}"

class Match(models.Model):
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('ongoing', 'Ongoing'),
		('completed', 'Completed'),
	]

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	tournament = models.ForeignKey(Tournament, related_name='matches', on_delete=models.CASCADE)
	round = models.IntegerField()
	player1 = models.ForeignKey(TournamentParticipant, on_delete=models.CASCADE, related_name='player1_matches')
	player2 = models.ForeignKey(TournamentParticipant, on_delete=models.CASCADE, related_name='player2_matches')
	start_time = models.DateTimeField(null=True, blank=True)
	end_time = models.DateTimeField(null=True, blank=True)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
	final_score = models.CharField(max_length=10, null=True, blank=True)
	winner = models.ForeignKey(TournamentParticipant, on_delete=models.SET_NULL, null=True, blank=True)
	

	def __str__(self):
		return f"Match {self.id}: Round {self.round}: {self.player1} vs {self.player2} - {self.status}"
	

	

# Score does not have a model, it is a field in the Match model
# Because the score records are not stored in the database, they are stored in the score field in the Match model
class Score(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='scores')
	# player = models.ForeignKey(User, on_delete=models.CASCADE)
	score = models.IntegerField()
	timestamp = models.DateTimeField(auto_now_add=True)