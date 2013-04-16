from forms import TournamentForm
# Create your views here.
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic.base import View
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.forms import ModelForm, ValidationError
from django.http import Http404
from wagers.models import Wager, Bet, WagerSettingSingleton
from django.contrib.auth.models import User
from django import forms
from decimal import Decimal
from models import Tournament

class AddTournament(CreateView):
    """
    People can add tournaments which they are then responsible for managing
    from this view.
    """
    model = Tournament
    template_name = "wagers/tournaments/add.html"
    
    def form_valid(self, form):
        """
        Adds a tournament to the database and makes sure to set 
        ``created_by`` to the currently logged in user. Redirects
        to tournament URL if form created succesfully. 
        """
        if form.is_valid():
            tourney = form.save(commit=False)
            tourney.created_by = self.request.user
            tourney.save()
            messages.add_message(self.request, messages.SUCCESS, "Tournament created!")      
        return super(AddTournament, self).form_valid(form)

class TournamentDetails(View):
    """
    Presents users with a view of the tournament and the admin of the
    tournament with an administration page.
    """
    template_name = "wagers/tournaments/details.html"
    def get(self, request, tourney_uuid):
        """
        Returns the details page for the tournament.
        """
        tourney = Tournament.objects.get(uuid=tourney_uuid)
        user_is_playing = tourney.is_user_playing(request.user)
        join_form = TournamentForm(initial={"uuid":tourney.uuid})
        return render(self.request,
                      self.template_name,
                      {"tourney": tourney,
                       "user_is_playing": user_is_playing,
                       "join_form": join_form})
                   
class JoinTournament(View):
    """
    This view handles the adding of a player into a tournament. It should only be
    usable by people who are already logged in.
    """
    def post(self, request):
        """
        Tries to add a player to a tournament.
        """
        form = TournamentForm(request.POST)
        if form.is_valid():
            uuid = form.cleaned_data["uuid"]
            tourney = form.get_tournament()
            if tourney.can_add_player(request.user):
                tourney.add_player(request.user)
                messages.add_message(self.request, messages.SUCCESS, "Joined tournament.")       
            else:
                error_message = "Couldn't join the tournament. Do you have enough credits or have you already joined?"
                messages.add_message(self.request, messages.ERROR, error_message)
            return redirect("tournament-details", uuid)
            
        # The only way someone should get here is if they tampered with the form.
        raise Http404
        

        

class WagerHistoryView(View):
    template_name = "wagers/wager_history.html"
    def get(self, request):
        bets = Bet.objects.filter(user=request.user)
        return render(self.request, self.template_name, {"bets": bets})

class WagerListView(View):
    template_name = "wagers/wager_list.html"
    def get(self, request):
        wagers = Wager.objects.all()
        bettable_wagers = wagers.exclude(bet__user=request.user).filter(is_open=True)
        return render(self.request, self.template_name, {"wagers": wagers,
                                                         "bettable_wagers": bettable_wagers})
class ResetEverythingView(View):
    def post(self, request):
        Wager.objects.all().delete()
        settings, created = WagerSettingSingleton.objects.get_or_create(id=1)
        for user in User.objects.all():
            profile = user.get_profile()
            profile.credits = settings.default_credits
            profile.save()
        messages.add_message(self.request, messages.SUCCESS, "Site reset.")
        return redirect("/")
            
class WagerCreateView(CreateView):
    model = Wager
    success_url = "/wagers/wagers/index/"

    def form_valid(self, form):
        print form.cleaned_data
        messages.add_message(self.request, messages.SUCCESS, "Wager created.")
        return super(CreateView, self).form_valid(form)

class WagerIDForm(forms.Form):
    id = forms.IntegerField()

class WagerDeleteForm(WagerIDForm): pass
    
class WagerDeleteView(View):
    def post(self, request):
        form = WagerDeleteForm(self.request.POST)
        if form.is_valid():    
            wager = Wager.objects.get(id=form.cleaned_data["id"])
            wager.delete()
            messages.add_message(request, messages.SUCCESS, 'Wager deleted.')
            return redirect(self.request.META["HTTP_REFERER"])
        
class WagerCloseForm(WagerIDForm): pass

class WagerCloseView(View):
    def post(self, request):
        form = WagerCloseForm(self.request.POST)
        if form.is_valid():    
            wager = Wager.objects.get(id=form.cleaned_data["id"])
            wager.is_open = False
            wager.save()
            messages.add_message(request, messages.SUCCESS, 'Wager closed.')
            return redirect(self.request.META["HTTP_REFERER"])

class WagerOpenForm(WagerIDForm): pass

class WagerOpenView(View):
    def post(self, request):
        form = WagerOpenForm(self.request.POST)
        if form.is_valid():    
            wager = Wager.objects.get(id=form.cleaned_data["id"])
            wager.is_open = True
            wager.save()
            messages.add_message(request, messages.SUCCESS, 'Wager opened.')
            return redirect(self.request.META["HTTP_REFERER"])
    



class WagerPayoutForm(forms.Form):
    position = forms.BooleanField(required=False)
    id = forms.IntegerField()

class Bookie():
    bets = []
    winning_position = None
    winner_pot_total = 0.0
    pot_total = 0.0
    
    def __init__(self, bets, winning_position):
        self.bets = bets
        self.winning_position = winning_position
        self.winner_pot_total = sum([bet.amount_bet for bet in bets if bet.position == self.winning_position])
        self.pot_total = sum([bet.amount_bet for bet in bets])

    def get_bets_with_returns(self):
        """Returns a list of dictionaries with the bet and the amount that the
        bet won.

        Returns [{"bet" : bet, "won" : float} ...]
        """
        winnings_dict_list = []
        for bet in self.bets:
            amount_won =  0.0
            if bet.position == self.winning_position:
                cut = bet.amount_bet / self.winner_pot_total
                amount_won = self.pot_total * cut
            winnings_dict_list.append({"bet": bet, "won": Decimal(amount_won)})
        return winnings_dict_list
            
class WagerPayoutView(TemplateView):
    template_name = "wagers/close.html"

    def post(self, request):
        form = WagerPayoutForm(request.POST)
        if form.is_valid():
            wager = Wager.objects.get(id=form.cleaned_data["id"])
            bets = wager.bet_set.all()
            bookie = Bookie(bets, form.cleaned_data["position"])
            winners = bookie.get_bets_with_returns()

            for winner in winners:
                profile = winner["bet"].user.get_profile()                            
                profile.credits = profile.credits + winner["won"]
                profile.save()

            wager.is_open = False
            wager.winning_position = form.cleaned_data["position"]
            wager.save()
        return redirect("/wagers/wagers/payout/?id=" + str(wager.id))

    def get_context_data(self, **kwargs):
        wager = Wager.objects.get(id=int(self.request.GET["id"]))
        bets = wager.bet_set.all()
        bookie = Bookie(bets, wager.winning_position)
        return {"winners": bookie.get_bets_with_returns, "wager": wager}


        
            
        
class BetForm(ModelForm):
    max_bet = 1
    class Meta:
        model = Bet

    def bet_too_little(self, credits_bet):
        return credits_bet <= 0

    def bet_too_much(self, credits_bet, credits_available):
        "Returns True if not enough credits or exceeded the maximum allowed bet."
        return credits_bet > credits_available and credits_bet > self.max_bet

    def is_valid(self, profile):
        valid = super(BetForm, self).is_valid()
        if valid:
            if not self.cleaned_data["on_prop"].is_open:
              valid = False
              self.errors["on_prop"] = ["This proposition is no longer open for bets."]
            available = profile.credits
            bet = self.cleaned_data["amount_bet"]
            if self.bet_too_little(bet) or self.bet_too_much(bet, available):
                valid = False
                self.errors["amount_bet"] = ["Not enough credits to make that bet."]
        return valid
        

class WagerView(TemplateView):
    template_name = "wagers/wager.html"

    def get_wager(self):
        try:
            return Wager.objects.get(id=int(self.request.GET['id']))
        except:
            raise Http404
        
    @method_decorator(login_required)
    def post(self, request):
        user = self.request.user
        wager = self.get_wager()
        form = BetForm(self.request.POST, initial={"user": user,
                                                   "on_prop": wager})    
        profile = self.request.user.get_profile()
        if form.is_valid(profile):
            # I don't want to let the users set what wager and user they are
            # since it would allow some clever hacks.
            if wager != form.cleaned_data["on_prop"] or user != form.cleaned_data["user"]:
                raise Htpp404
            
            position=form.cleaned_data["position"]
            amount_bet=form.cleaned_data["amount_bet"]

            credits = profile.credits    
            profile.credits = credits - amount_bet
            profile.save()
            bet = Bet(on_prop=wager,
                        user=user,
                        amount_bet=amount_bet,
                        position=position)
            bet.save()
            messages.add_message(self.request, messages.SUCCESS, "Bet made.")
            return redirect("/wagers/wagers/index/")
        else:
            return render(self.request, self.template_name, {"form": form,
                                                             "wager": wager})

    def get_bet_form(self):
        return BetForm(initial={"user": self.request.user,
                                "on_prop": self.get_wager(),
                                "amount_bet": 1})
        

        
    def get_context_data(self, **kwargs):
        return {'wager': self.get_wager(), "form": self.get_bet_form()}
