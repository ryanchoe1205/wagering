from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import models
from fields import UUIDField

class Tournament(models.Model):
    """
    Gambling is illegal, but having a competition to see who gambles best
    isn't. The tournament model is used to segment the site into silos of
    props which users can bet on.
    
    Users buy into tournaments. The winners of the tournament are paid out
    from the entrace fees. The house takes a small cut of this entrace fee
    to support the operation and development of the site.
    """
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)
    
    is_public_help = "Check this to let anyone find your tournament."
    is_public = models.BooleanField(default=False, help_text=is_public_help)
    # This is an auto-generated field used to link to tournaments. The idea is
    # that it makes it much harder for people to join private tournaments by
    # iterating through tournament ids.
    uuid = UUIDField(auto=True)
    
    # When the tournament winners are paid out, the tournament is closed to
    # further interaction.
    is_open = models.BooleanField(default=True)
    
    # Ideally the tournament names shouldn't wrap around on most screen sizes.
    # If they do the CSS and max_length should be adjusted.
    name_help = "A good name tells people what sports will be bet on."
    name = models.CharField(max_length=50, help_text=name_help)
    
    entrance_fee_help = "A good entrance fee won't bankrupt people."
    entrance_fee = models.DecimalField(decimal_places=10,
                                       max_digits=100,
                                       default=5.0,
                                       help_text=entrance_fee_help,
                                       editable=False)
    
    # This should only be changed by using methods.
    prize_pool = models.DecimalField(decimal_places=10,
                                     max_digits=100,
                                     default=0.0)
    
    def add_player(self):
        """
        Adds a player to the tournament and collects their entrance fee.
        
        Throws an exception if the user doesn't have enough money to enter
        the tournament. Returns True if the player joins the tournament.
        """
        pass
        
    def is_closable(self):
        """
        Returns true if all of the tournaments currently active props have 
        been closed and payed out.
        """
        pass
    
    def close_tournament(self):
        """
        Pays out the winners and closes the tournament.
        """
        pass


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


