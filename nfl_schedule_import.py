from django.core.management import setup_environ
import wagering.settings
setup_environ(wagering.settings)

from game_database.models import Game
from game_database.scraper import scrape_nfl_schedule

games = scrape_nfl_schedule(2013)
for game in games:
    db_game = Game(**game)
    db_game.save()