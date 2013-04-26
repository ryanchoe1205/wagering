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
