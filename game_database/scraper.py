import urllib2
import datetime
import json
from pytz import timezone


base_url = "http://mlb.mlb.com/components/schedule/schedule_{0}.json"

def build_url(date):
    return base_url.format(date.strftime("%Y%m%d")) 

def get_page(url):
    return urllib2.urlopen(url).read()

def process_game(game):
	game_dict = {}
	game_dict["team_a"] = game["home"]["full"]
	game_dict["team_b"] = game["away"]["full"]
	game_dict["team_a_aux_1"] = game["home"]["probable"]
	game_dict["team_b_aux_1"] = game["away"]["probable"]
	game_dict["game_type"] = game["sport_code"]

	start_time = game["game_time"][:10]
	start_time = datetime.datetime.fromtimestamp(int(start_time))
	eastern = timezone("US/Eastern")
	start_time = eastern.localize(start_time)
	game["start_time"] = start_time


	score_a = game["home"]["result"]
	score_b = game["away"]["result"]
	is_finished = score_a is not None and score_b is not None
	if is_finished:
		if score_a == score_b:
			outcome = "Drawn"
		elif score_a > score_b:
			outcome = "Won"
		else:
			outcome = "Lost"
	else:
		outcome = "N/A"

	game_dict["team_a_score"] = score_a
	game_dict["team_b_score"] = score_b
	game_dict["is_finished"] = is_finished
	game_dict["outcome"] = outcome

	return game_dict

def get_games_on(date):
	url = build_url(date)
	page = get_page(url)
	games = json.loads(page)
	return map(process_game, games)

