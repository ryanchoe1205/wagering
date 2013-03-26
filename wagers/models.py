from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import models

class EditableHTML(models.Model):
    html = models.TextField()

class Wager(models.Model):
    proposition = models.TextField()
    is_open = models.BooleanField(default=True)
    winning_position = models.BooleanField(default=True)

class Bet(models.Model): 
    amount_bet = models.DecimalField(decimal_places=10, max_digits=100)
    on_prop = models.ForeignKey("Wager")
    user = models.ForeignKey(User)
    position = models.BooleanField()

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    credits = models.DecimalField(decimal_places=10, max_digits=100)

def create_user_profile(sender, instance, created, **kwargs):
    if created: UserProfile.objects.get_or_create(user=instance, credits=100.0)

post_save.connect(create_user_profile, sender=User)


