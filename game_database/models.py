from django.db import models

class Game(models.Model):
	game_type = models.CharField(max_length=10)
	start_time = models.DateTimeField()
	
	team_a = models.CharField(max_length=80)
	team_a_aux_info_1 = models.CharField(max_length=144)
	team_a_score = models.IntegerField(null=True)

	team_b = models.CharField(max_length=80)
	team_b_aux_info_1 = models.CharField(max_length=144)
	team_b_score = models.IntegerField(null=True)

	is_finished = models.BooleanField()
	# Won if team a wins, Lost if team b wins, Drawn if a draw, N/A if not finished
	outcome = models.CharField(max_length=5, blank=True)

	def __str__(self):
		return self.team_a + " vs " + self.team_b