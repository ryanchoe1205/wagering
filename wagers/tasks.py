from celery import task
from wagers.models import Wager

@task()
def open_wager(wager_id):
    wager = Wager.objects.get(id=wager_id)
    wager.is_open = True
    wager.save()

@task()
def close_wager(wager_id):
    wager = Wager.objects.get(id=wager_id)
    wager.is_open = False
    wager.save()
