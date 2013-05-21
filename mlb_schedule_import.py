from django.core.management import setup_environ
import wagering.settings
setup_environ(wagering.settings)

from game_database.models import Game


def add_game(team_a, team_b, start_time):
	game = Game(game_type="MLB", 
				team_a=team_a,
				team_b=team_b,
				start_time=start_time,
				is_finished=False)
	game.save()

import csv
import datetime
import urllib2

url = "https://dl.dropboxusercontent.com/u/2537320/MLB_schedule1M.csv"
csv_file = urllib2.urlopen(url)
csv_reader = csv.reader(csv_file)
next(csv_reader, None) # Skip the headers

for row in csv_reader:
	try:
		# ['DATE', 'AWAY', 'HOME', 'TIME', 'AWAY PITCHER', 'HOME PITCHER', '']
		# Date formatting is '21-May' + '-2013'
		date_str = row[0] + '-2013'
		# Time formatting is 7:05pm or GM n: 7:05pm
		time_str = row[3]
		if "GM" in time_str:
			time_str = time_str[6:]
		if "TBD" in time_str:
			raise ValueError("No time given.", row)

		datetime_str = date_str + ' ' + time_str
		start_time = datetime.datetime.strptime(datetime_str, "%d-%b-%Y %I:%M%p")
		team_a = row[1]
		team_b = row[2]
		add_game(team_a, team_b, start_time)
	except Exception as e:
		print e
		print time_str

print "Running file."

