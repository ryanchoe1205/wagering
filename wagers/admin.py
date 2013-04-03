from django.contrib import admin
from wagers.models import WagerSettingSingleton, Wager
admin.site.register(WagerSettingSingleton)
admin.site.register(Wager)

