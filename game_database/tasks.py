from celery import task
from game_database.models import Game
from game_database.scraper import get_games_on, get_nfl_games_on
import datetime
from django.utils import timezone

def get_game(game):
	return Game.objects.get(start_time__year=game["start_time"].year,
					 		start_time__month=game["start_time"].month,
					 		start_time__day=game["start_time"].day,
					 		team_a=game["team_a"],
					 		team_b=game["team_b"])

def update_db_from(game):
	db_game = get_game(game)
	if db_game:
		game["start_time"] = db_game.start_time
		db_game.update(game)
		db_game.save()
	else:
		db_game = Game(game)
		db_game.save()

@task()
def scrape_mlb():
	today = timezone.now()
	days = [today, today-datetime.timedelta(days=1), today-datetime.timedelta(days=2)]
	for day in days:
		games = get_games_on(day)
		for game in games:
			update_db_from(game)

@task()
def scrape_nfl():
	today = timezone.now()
	days = [today, today-datetime.timedelta(days=1), today-datetime.timedelta(days=2)]
	for day in days:
		games = get_nfl_games_on(day)
		for game in games:
			update_db_from(game)
