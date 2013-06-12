from celery import task
import datetime
from wagers.models import Proposition
from wagers.models import Schedule
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
		props = Proposition.objects.filter(schedule=schedule_id)
		for prop in props:
			prop.close()
			prop.save()

# @task()
# def pay_props(date):
# At the end of each day...
# For every proposition built using the game database
# That closed automatically over the course of the last week
# That has not yet been paid out
# Figure out who won and pay out the proposition
# If you can't figure it out, then do nothing
