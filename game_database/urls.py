from django.conf.urls import patterns, url
from views import Schedule
from views import GetGameByID

urlpatterns = patterns('',
    url('^schedule/', Schedule.as_view(), name="schedule"),
    url('^game/', GetGameByID.as_view(), name="game-by-id"))