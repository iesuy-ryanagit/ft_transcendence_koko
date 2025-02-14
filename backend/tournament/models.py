import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

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
	max_players = models.IntegerField()
	winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	current_round = models.IntegerField(default=1)
	
	def __str__(self):
		return f"{self.name} - {self.status}"


class Match(models.Model):
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('ongoing', 'Ongoing'),
		('completed', 'Completed'),
	]

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	tournament = models.ForeignKey(Tournament, related_name='matches', on_delete=models.CASCADE)
	round = models.IntegerField()
	player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player1_matches')
	player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player2_matches')
	start_time = models.DateTimeField(null=True, blank=True)
	end_time = models.DateTimeField(null=True, blank=True)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
	score = models.CharField(max_length=10, null=True, blank=True)
	

	def __str__(self):
		return f"Match {self.id}: Round {self.round}: {self.player1} vs {self.player2} - {self.status}"