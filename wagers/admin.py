from django.contrib import admin
from wagers.models import Tournament, WagerSettingSingleton, Wager
admin.site.register(Tournament)
admin.site.register(WagerSettingSingleton)
admin.site.register(Wager)

