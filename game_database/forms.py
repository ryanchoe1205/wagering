from django import forms
from models import Game

class ScheduleForm(forms.Form):
	"""
	A form used to validate inputs on requests that want to filter by schedule
	and game type.
	"""
	GAME_TYPES = ["MLB", "NBA", "NFL", "NHL", "UFC", "MLS"]

	MLB = forms.BooleanField(required=False)
	NBA = forms.BooleanField(required=False)
	NFL = forms.BooleanField(required=False)
	NHL = forms.BooleanField(required=False)
	UFC = forms.BooleanField(required=False)
 	MLS = forms.BooleanField(required=False)
 	start_time = forms.DateTimeField()
 	end_time = forms.DateTimeField()

	def get_game_type(self):
		"""
		Returns a list of all the games that the requesting party claimed to be
		interested in.
		"""
		game_types = []
		for game_type in self.GAME_TYPES:
			if self.cleaned_data[game_type]:
				game_types.append(game_type)
		return game_types

def validate_game_exists(id):
	"""
	Validator to ensure that the given game ID corresponds to a game
	in the database.
	"""
	try:
		game = Game.objects.get(pk=id)
	except:
		raise forms.ValidationError("No game with that id exists.")

class GameForm(forms.Form):
	"""
	A form used to get a single instance of a Game through its ID.
	"""
	id = forms.IntegerField(validators=[validate_game_exists])

	def get_game(self):
		"""
		Returns the game in the database that the ID in the form corresponds
		to.
		"""
		return Game.objects.get(pk=self.cleaned_data.get("id")).__dict__
	

