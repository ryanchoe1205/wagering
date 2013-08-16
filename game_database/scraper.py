import BeautifulSoup
import urllib2
import datetime
import json
from pytz import timezone
from dateutil import parser

# MLB Scraper

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
 	game_dict["outcome"] = outcome

	return game_dict

def get_games_on(date):
	url = build_url(date)
	page = get_page(url)
	games = json.loads(page)
	return map(process_game, games)

# NFL Scraper
nfl_base_url = "http://www.nfl.com/schedules/"

def build_nfl_url(year, type, week):
	end = str(year) + "/" + type + str(week)
	return nfl_base_url + end

def build_nfl_urls(year):
	urls = []

	# Regular season URLS
	for week in range(1, 18):
		urls.append(build_nfl_url(year, "REG", week))
	
	# Pre season URLS
	for week in range(1, 5):
		urls.append(build_nfl_url(year, "PRE", week))
	return urls

def scrape_nfl_url(url):
	page = get_page(url)
	soup = BeautifulSoup.BeautifulSoup(page)

	schedules_list = soup.findAll("ul", attrs="schedules-table")
	if len(schedules_list) == 2:
		schedules_list = schedules_list[1]
	else:
		schedules_list = schedules_list[0]
	schedule_date = False
	games_list = []

	for list_item in schedules_list.findAll("li"):
		if "schedules-list-date" in list_item["class"] and "Next Game" not in list_item.text:
			schedule_date = list_item.find("span").text
		elif schedule_date and "schedules-list-matchup":
			game = list_item
			game_dict = {}
			more_game = game.find("div", attrs={"class": "list-matchup-row-team"})
			game_dict["team_a"] = (more_game.find("span", attrs={"class": "team-name away "}) or more_game.find("span", attrs={"class": "team-name away lost"})).text
			game_dict["team_b"] = (more_game.find("span", attrs={"class": "team-name home "}) or more_game.find("span", attrs={"class": "team-name home lost"})).text
			game_dict["game_type"] = "NFL"

			time = game.find("span", attrs={"class": "time"}).text
			game_dict["is_finished"] = "FINAL" in time
			if not game_dict["is_finished"]:
				pm = game.find("span", attrs={"class": "pm"}).text
				match_date = schedule_date + " " + time + " " + pm
				game_dict["team_a_score"] = None
				game_dict["team_b_score"] = None
			else:
				game_dict["team_a_score"] = int((more_game.find("span", attrs={"class": "team-score away "}) or more_game.find("span", attrs={"class": "team-score away lost"})).text)
				game_dict["team_b_score"] = int((more_game.find("span", attrs={"class": "team-score home "}) or more_game.find("span", attrs={"class": "team-score home lost"})).text)
				match_date = schedule_date
			if game_dict["is_finished"]:
				if game_dict["team_a_score"] == game_dict["team_b_score"]:
					outcome = "Drawn"
				elif game_dict["team_a_score"] > game_dict["team_b_score"]:
					outcome = "Won"
				else:
					outcome = "Lost"
			else:
				outcome = "N/A"

			game_dict["outcome"] = outcome
			date = parser.parse(match_date)
			eastern = timezone("US/Eastern")
			date = eastern.localize(date)
			game_dict["start_time"] = date
			games_list.append(game_dict)
	return games_list

def scrape_nfl_schedule(year):
	urls = build_nfl_urls(year)
	games = []
	for url in urls:
		games.extend(scrape_nfl_url(url))
	return games


def get_nfl_games_on(date):
	games = scrape_nfl_schedule(2013)
	games_on_day = []
	for game in games:
		if game["start_time"].date() == date.date():
			games_on_day.append(game)
	return games_on_day




