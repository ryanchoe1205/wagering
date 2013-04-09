from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import models

class WagerSettingSingleton(models.Model):
    default_credits = models.DecimalField(decimal_places=10, max_digits=100, default=10)

    def save(self, *args, **kwargs):
        self.id = 1
        super(WagerSettingSingleton, self).save(*args, **kwargs)

    def delete(self):
        pass
        
class EditableHTML(models.Model):
    html = models.TextField()

class Wager(models.Model):
    is_open = models.BooleanField(default=True)
    winning_position = models.BooleanField(default=True) # winning_position means team_a won
    team_a = models.TextField()
    team_b = models.TextField()
    notes = models.TextField()
    open_wager_at = models.DateTimeField(blank=True, null=True)
    close_wager_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
      return self.team_a + " vs " + self.team_b
      
def wager_automation(sender, instance, created, **kwargs):
    from wagers.tasks import open_wager
    from wagers.tasks import close_wager
    if created:
        if instance.open_wager_at:
            open_wager.apply_async(args=[instance.id], eta=instance.open_wager_at)
        if instance.close_wager_at:
            close_wager.apply_async(args=[instance.id], eta=instance.close_wager_at)
 
post_save.connect(wager_automation, sender=Wager)

            

class Bet(models.Model): 
    amount_bet = models.DecimalField(decimal_places=10, max_digits=100)
    on_prop = models.ForeignKey("Wager")
    user = models.ForeignKey(User)
    position = models.BooleanField()

    class Meta():
        unique_together = [("user", "on_prop")]

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    credits = models.DecimalField(decimal_places=10, max_digits=100)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        wager_settings, created = WagerSettingSingleton.objects.get_or_create(id=1)
        profile, created = UserProfile.objects.get_or_create(user=instance, credits=wager_settings.default_credits)
        profile.save()

post_save.connect(create_user_profile, sender=User)


