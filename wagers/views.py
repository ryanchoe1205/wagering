# Create your views here.
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import View
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.forms import ModelForm, ValidationError
from django.http import Http404
from wagers.models import Wager, Bet
from django import forms
from django.shortcuts import redirect
from decimal import Decimal 

class WagerCreateView(CreateView):
    model = Wager
    success_url = "/wagers/wagers/index/"

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, "Wager created.")
        return super(CreateView, self).form_valid(form)

class WagerDeleteForm(forms.Form):
    id = forms.IntegerField()
    
class WagerDeleteView(View):
    def post(self, request):
        form = WagerDeleteForm(self.request.POST)
        if form.is_valid():    
            wager = Wager.objects.get(id=form.cleaned_data["id"])
            wager.delete()
            messages.add_message(request, messages.SUCCESS, 'Wager deleted.')
            return redirect(self.request.META["HTTP_REFERER"])


class WagerCloseForm(forms.Form):
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
            
class WagerCloseView(TemplateView):
    template_name = "wagers/close.html"

    def post(self, request):
        form = WagerCloseForm(request.POST)
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
        return redirect("/wagers/wagers/closed?id=" + str(wager.id))

    def get_context_data(self, **kwargs):
        wager = Wager.objects.get(id=int(self.request.GET["id"]))
        bets = wager.bet_set.all()
        bookie = Bookie(bets, wager.winning_position)
        return {"winners": bookie.get_bets_with_returns, "wager": wager}


        
            
        
class BetForm(ModelForm):
    class Meta:
        model = Bet
        fields = ("position", "amount_bet")
            
        
class WagerView(TemplateView):
    template_name = "wagers/wager.html"

    def get_wager(self):
        try:
            return Wager.objects.get(id=int(self.request.GET['id']))
        except:
            raise Http404

    def post(self, request):
        if not self.request.user.is_authenticated():
            redirect("login")

        form = self.get_bet_form()
        wager = self.get_wager()
        user = self.request.user
        if form.is_valid():
            position=form.cleaned_data["position"]
            amount_bet=form.cleaned_data["amount_bet"]

            profile = self.request.user.get_profile()
            credits = profile.credits
            if not(amount_bet <= 0 or amount_bet > credits):          
                profile.credits = credits - amount_bet
                profile.save()
                bet = Bet(on_prop=wager, user=user, amount_bet=amount_bet, position=position)
                bet.save()
     
        return redirect(self.request.META["HTTP_REFERER"])

    def get_bet_form(self):
        return BetForm(self.request.POST)
        
    def get_context_data(self, **kwargs):
        return {'wager': self.get_wager(), "form": self.get_bet_form()}
