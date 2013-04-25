from django.contrib import admin
from models import Tournament
from models import Proposition
from models import Bet
from models import WagerSettingSingleton

admin.site.register(Tournament)
admin.site.register(Proposition)
admin.site.register(Bet)
admin.site.register(WagerSettingSingleton)

