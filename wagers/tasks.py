from celery import task
from wagers.models import Proposition

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

# @task()
# def pay_props(date):
# At the end of each day...
# For every proposition built using the game database
# That closed automatically over the course of the last week
# That has not yet been paid out
# Figure out who won and pay out the proposition
# If you can't figure it out, then do nothing
