from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import models
from django.core.urlresolvers import reverse
from fields import UUIDField
from decimal import Decimal
from helpers import take_while

class Player(models.Model):
    """
    Each tournament is made up of site Users, but the money that a User has is
    not the money they use while playing in any given tournament. The player
    class is used to work with users as they play in tournaments. It keeps
    track of the money that a player has available in each tournament.
    """
    tournament = models.ForeignKey("Tournament")
    user = models.ForeignKey(User)
    
    class Meta:
        unique_together = [("tournament", "user")]
    
    # This is the amount of money the user has available for betting.
    credits = models.DecimalField(decimal_places=10, max_digits=100)
    
    def __str__(self):
        """
        Returns a string representation of the player object for use in the admin.
        """
        return str(self.user)
    
    def is_user_player(self, user):
        """
        Returns True if the user is the player. False otherwise. This should be used
        to validate that the player is who they claim to be when making bets.
        """
        return self.user == user
        
    def can_afford_bet(self, credits):
        """
        Returns whether the user has enough credits to cover the bet.
        """
        return self.credits >= credits
    
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
    created_by = models.ForeignKey(User, editable=False)
    
    # Ideally the tournament names shouldn't wrap around on most screen sizes.
    # If they do the CSS and max_length should be adjusted.
    name_help = "A good name tells people what sports will be bet on."
    name = models.CharField(max_length=50, help_text=name_help)
    
    # This is used to decide whether or not the wager should be included in
    # lits of currently open tournaments.
    is_public_help = "Check this to let anyone find your tournament."
    is_public = models.BooleanField(default=False, help_text=is_public_help)

    # When the tournament winners are paid out, the tournament is closed to
    # further interaction. The prize pool itself is the amount which will be
    # split up and paid to the winners. The prize pool itself is the entrance
    # fees, minus the cut that the house takes.
    entrance_fee_help = "A good entrance fee won't bankrupt people."
    entrance_fee = models.DecimalField(decimal_places=10,
                                       max_digits=100,
                                       default=5.0,
                                       help_text=entrance_fee_help)
    is_open = models.BooleanField(default=True, editable=False)
    is_paid = models.BooleanField(default=False, editable=False)
    prize_pool = models.DecimalField(decimal_places=10,
                                     max_digits=100,
                                     default=0.0,
                                     editable=False)
                                     
    # This is an auto-generated field used to link to tournaments. The idea is
    # that it makes it much harder for people to join private tournaments by
    # iterating through tournament ids.
    uuid = UUIDField(auto=True)
    
    starting_credits_help = "This is how many credits people start the tournament with."
    starting_credits = models.DecimalField(decimal_places=10,
                                           max_digits=100,
                                           default=10.0,
                                           help_text=starting_credits_help)
    
    def __str__(self):
        """
        Returns the name of the tournament for rendering.
        """
        return self.name
        
    def is_user_admin(self, user):
        """
        Returns True if the given user is the one who created the tournament.
        This should be used to make sure that only the tournament admin can
        make important changes to the tournament like adding props, closing
        props, and other adminsistrative duties.
        """
        return user == self.created_by
    
    def can_add_player(self, user):
        """
        Returns True if the user can join the tournament.
        """
        user_profile = user.get_profile()
        if user_profile.credits < self.entrance_fee:
            return False
        if self.is_user_playing(user):
            return False
        return True
        
    def add_player(self, user):
        """
        Adds a player to the tournament and collects their entrance fee.
        
        Throws a ValueError if the user can't play in the tournament.
        
        Returns True if the player joins the tournament.
        """
        # Make sure the user can play
        user_profile = user.get_profile()
        if user_profile.credits < self.entrance_fee:
            raise ValueError("Not enough credits to pay entrance fee.")
        if self.is_user_playing(user):
            raise ValueError("User already in tournament.")
        
        # Handle the money transfer to join the tournament
        user_profile.credits = user_profile.credits - self.entrance_fee
        user_profile.save()
        self.prize_pool = self.prize_pool + self.entrance_fee
        self.save()
        
        # Join the tournament
        new_player = Player(user=user,
                            tournament=self,
                            credits=self.starting_credits)
        new_player.save()
        return True
       
    
    def is_user_playing(self, user):
        """
        Returns the Player if the given User is a Player. Otherwise None.
        """
        try:
            return self.player_set.get(user=user)
        except Player.DoesNotExist:
            return None
              
    def is_closable(self):
        """
        Returns true if all of the tournaments currently active props have 
        been closed and payed out.
        """
        return all([prop.is_paid for prop in self.proposition_set.all()])
    
    def get_payout_information(self):
        """
        Returns the payout information for the players in the tournament. In a list of dicts
        of the form {"players": players, "place": place, "won": won}. It is possible for users
        to tie. In the event of ties everyone below them will be one place farther down. Any
        prize money in the places that the players occupy will be split between them.
        """
        players = self.player_set.all().order_by("credits")
        if len(players) < 3:
            winner_cut = [1]
        else:
            winner_cut = [.6, .3, .1]
        
        # Constructs the list of placings
        place = 0
        placing_list = []
        while place < len(players):
            # Use the next player for the purpose of dealing with ties.
            next_player = players[place]
            is_same_place = lambda x: next_player.credits == x.credits
            
            # Get a list of all people who ended up tying at this place
            same_place = take_while(players[place:], is_same_place)
            
            # Compute the amount of money this group should win
            prize_cut = sum(winner_cut[place:place+len(same_place)])
            shared_pot = prize_cut * self.prize_pool / len(same_place)
            
            # Add the informationa bout this place to the place listings.
            placing_list.append({"players": same_place, "won": shared_pot, "place": place})
            
            # Move to the next unplaced player.
            place += len(same_place)
        return placing_list
    
    def payout(self):
        """
        Closes and pays out the tournament.
        """
        if not self.is_closable():
            raise ValueError("The tournament can't be closed.")
        if self.is_paid:
            raise ValueError("This tournament has already been paid out.")
        payout_information = self.get_payout_information()
        for info in payout_information:
            players, cut = info["players"], info["won"]
            for player in players:
                user_profile = player.user.get_profile()
                user_profile.credits += cut
                user_profile.save()
        self.is_open = False
        self.is_paid = True
        self.save()
        
    def get_absolute_url(self):
        """
        Returns a URL that leads to this tournament's details page..
        """
        return reverse('tournament-details', args=[self.uuid])

class Proposition(models.Model):
    """
    Each tournament is a competition to see who has the best predictive capabilities.
    The people playing are trying to predict the outcome of each proposition. Since
    this is (at the time of writing) a sports betting site, the wagers will be on
    whether one team will beat another team.
    """
    created_on = models.DateTimeField(auto_now_add=True)
    tournament = models.ForeignKey(Tournament)
    
    team_help_text = "A team that people will be betting for or against."
    team_a = models.CharField(max_length=50, help_text=team_help_text)
    team_b = models.CharField(max_length=50, help_text=team_help_text)
    notes_help_text = "Notes will be visible to users."
    notes = models.CharField(max_length=100, help_text=notes_help_text)
    
    is_open = models.BooleanField(default=True)
    open_help_text = "It is possible to schedule the prop to appear at a specific time."
    open_wager_at = models.DateTimeField(blank=True, null=True, help_text=open_help_text)
    close_help_text = "The prop can be scheduled to be closed to further betting too."
    close_wager_at = models.DateTimeField(blank=True, null=True, help_text=close_help_text)
    
    # These fields are used to determine the winning position of the proposition and whether
    # the proposition has been paid out.
    outcome = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False, editable=False)
    
    # This field marks how much money was in the pot of this proposition.
    pot = models.DecimalField(decimal_places=10, max_digits=100, default=0.0, editable=False)
    
    def __str__(self):
        """
        Returns a string representation of the prop.
        """
        return self.team_a + " vs " + self.team_b
    
    def get_payout_information(self):
        """
        Computes the payout information for the proposition.
        
        Returns a lists of dictionaries of the form: {"bet" bet, "won": credits}.
        """
        winners = self.bet_set.filter(position=self.outcome)
        winner_pot_total = sum([winner.credits for winner in winners])
        winning_dicts = []
        for bet in self.bet_set.all():
            amount_won = Decimal(0.0)
            if bet.position == self.outcome:
                cut = winner.credits / winner_pot_total
                amount_won = self.pot * cut
            winning_dicts.append({"bet": bet, "won": amount_won})
        return winning_dicts
    
    def payout(self):
        """
        Pays out the proposition. Closes it if it is open.
        """
        self.is_open = False
        if self.is_paid:
            raise ValueError("Already paid out the wager.")
        self.is_paid = True
        payouts = self.get_payout_information()
        for info in payouts:
            bet, credits = info["bet"], info["won"]
            player = bet.created_by
            player.credits += credits
            player.save()
        self.save()       
        
    def is_open_for_betting(self):
        """
        Returns whether the proposition is open for betting.
        """
        return self.is_open
    
    def has_player_bet(self, player):
        """
        Returns the Bet if the given Player has already made a bet
        in this tournament. Otherwise returns None.
        """
        try:
            return self.bet_set.get(created_by=player)
        except Bet.DoesNotExist:
            return None
    
    def can_player_bet(self, player):
        if player.tournament != self.tournament:
            return False
        elif self.has_player_bet(player):
            return False
        elif not self.is_open:
            return False
        return True
    
    def make_bet(self, bet):
        """
        Handles everything regarding the making of a bet in this prop.
        """
        player = bet.created_by
        if not self.can_player_bet(player):
            raise ValidationError("Not able to make a bet.")
        if not player.can_afford_bet(bet.credits):
            raise ValidationError("Not enough credits.")
        bet.save()
        player.credits -= bet.credits
        player.save()
        self.pot += bet.credits
        self.save()

        
class Bet(models.Model):
    """
    Each proposition can be bet on. The bet models ties bets to the player who made them.
    It also keepts track of what side of the prop the player predicted would be the
    eventual outcome.
    """
    created_by = models.ForeignKey("Player")
    credits = models.DecimalField(decimal_places=10, max_digits=100)
    proposition = models.ForeignKey("Proposition")
    
    # The side of the proposition the user thought would win.
    position = models.BooleanField()

    class Meta():
        unique_together = [("created_by", "proposition")]

class WagerSettingSingleton(models.Model):
    default_credits = models.DecimalField(decimal_places=10, max_digits=100, default=10)

    def save(self, *args, **kwargs):
        self.id = 1
        super(WagerSettingSingleton, self).save(*args, **kwargs)

    def delete(self):
        pass
        
class EditableHTML(models.Model):
    html = models.TextField()

            



class UserProfile(models.Model):
    user = models.OneToOneField(User)
    credits = models.DecimalField(decimal_places=10, max_digits=100)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        wager_settings, created = WagerSettingSingleton.objects.get_or_create(id=1)
        profile, created = UserProfile.objects.get_or_create(user=instance, credits=wager_settings.default_credits)
        profile.save()

post_save.connect(create_user_profile, sender=User)


