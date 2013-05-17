from django.db import models

# Create your models here.
class Game(models.Model):
	game_type = models.CharField(max_length=10)
	start_time = models.DateTimeField()
	team_a = models.CharField(max_length=80)
	team_b = models.CharField(max_length=80)

	is_finished = models.BooleanField()
	# Won if team a wins, Loss if team b wins, Draw if a draw, N/A if not finished
	outcome = models.CharField(max_length=5, blank=True)