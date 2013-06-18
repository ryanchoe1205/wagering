from celery import task
import datetime
from wagers.models import Proposition
from wagers.models import Schedule
from game_database.models import Game
from django.utils import timezone

@task()
def open_prop(prop_id):
    prop = Proposition.objects.get(id=prop_id)
    prop.open()
    prop.save()


@task()
def close_prop(prop_id):
    prop = Proposition.objects.get(id=prop_id)
    prop.close()
    prop.save()

def is_close_to_now(dt):
	"""
	Returns True if the datetime is within four minutes from the current time.
	Otherwise returns False.
	"""
	now = timezone.now()
	two_minutes_ago = now - datetime.timedelta(minutes=2)
	two_minutes_from_now = now + datetime.timedelta(minutes=2)
	return two_minutes_ago < dt < two_minutes_from_now

@task()
def open_props(schedule_id):
	schedule = Schedule.objects.get(id=schedule_id)
	if schedule.open_wager_at and is_close_to_now(schedule.open_wager_at):
		props = Proposition.objects.filter(schedule=schedule)
		for prop in props:
			prop.open()
			prop.save()

@task()
def close_props(schedule_id):
	schedule = Schedule.objects.get(id=schedule_id)
	if schedule.close_wager_at and is_close_to_now(schedule.close_wager_at):
		props = Proposition.objects.filter(schedule=schedule)
		for prop in props:
			prop.close()
			prop.save()

def pay_prop(prop):
	"""
	Given a prop, this finds out if it can be paid out programatically and if
	it can it does so.
	"""
	if prop.schedule.game_database_id:
		game = Game.objects.get(id=prop.schedule.game_database_id)
		if game.is_finished:
			if game.outcome == "Won":
				prop.outcome = True
				prop.payout()
			elif game.outcome == "Lost":
				prop.outcome = False
				prop.payout()

@task()
def pay_props():
	"""
	Gets all the props that need to be paid out and tries to pay them out.
	"""
	today = timezone.now()
	last_week = today - datetime.timedelta(days=7)
	props_closed_this_week = Proposition.objects.filter(schedule__close_wager_at__range=(last_week, today))
	that_were_auto_generated = props_closed_this_week.exclude(schedule__game_database_id=None)
	that_are_not_paid = that_were_auto_generated.filter(is_paid=False)
	props = that_are_not_paid
	for prop in props:
		pay_prop(prop)


