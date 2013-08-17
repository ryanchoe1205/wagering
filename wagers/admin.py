from django.contrib import admin
from models import Tournament
from models import Proposition
from models import Bet
from models import WagerSettingSingleton
from models import Schedule
from models import GameSeason

admin.site.register(Tournament)
admin.site.register(Proposition)
admin.site.register(Bet)
admin.site.register(WagerSettingSingleton)
admin.site.register(Schedule)
admin.site.register(GameSeason)


