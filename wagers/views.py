from django.http import HttpResponseForbidden
from django.http import Http404
from forms import TournamentForm
from forms import PropositionForm
from forms import PropositionAdminForm
from forms import PropositionPayoutForm
from forms import BetForm
from models import Tournament
from models import Proposition
from models import Player
from models import Bet
from models import WagerSettingSingleton
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic.base import View
from django.views.generic import CreateView


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

class OpenTournamentList(View):
    """
    This presents users with a view of the tournaments which they can join.
    """
    template_name = "wagers/tournaments/open-list.html"
    def get(self, request):
        tournaments = Tournament.objects.filter(is_open=True).order_by("-created_on")
        return render(self.request, self.template_name, {"tournaments": tournaments})

class ActiveTournamentList(View):
    """
    This presents users with a view of the tournaments they are currently active in.
    """
    template_name = "wagers/tournaments/active-list.html"
    def get(self, request):
        players = Player.objects.filter(user=request.user, tournament__is_open=True)
        return render(self.request, self.template_name, {"players": players})

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
        try:
            player = Player.objects.get(tournament=tourney, user=request.user)
        except:
            player = None
        join_form = TournamentForm(initial={"uuid":tourney.uuid})
        user_is_admin = tourney.is_user_admin(request.user)

        add_prop_form = PropositionForm(initial={"tournament":tourney.id})
        propositions = Proposition.objects.filter(tournament=tourney)
        bettable_props = propositions.exclude(bet__created_by=player).filter(is_open=True)
        return render(self.request,
                      self.template_name,
                      {"tourney": tourney,
                       "bettable_props": bettable_props,
                       "propositions": propositions,
                       "player": player,
                       "tournament_form": join_form,
                       "user_is_admin": user_is_admin,
                       "add_prop_form": add_prop_form})
                   
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
        
class PayoutTournament(View):
    def get(self, request):
        pass
    
    def post(self, request, tourney_uuid):
        """
        Tries to add a proposition to the tournament.
        """
        tourney = Tournament.objects.get(uuid=tourney_uuid)
        # Make sure that the user has admin rights for this tourney.
        if not tourney.is_user_admin(request.user):
            return HttpResponseForbidden("Only the tournament administrator can do that.")
        form = TournamentForm(request.POST)
        if form.is_valid():
            # Make sure the input wasn't a lie.
            tourney2 = form.get_tournament()
            if not tourney == tourney2:
                return HttpResponseForbidden("Only the tournament administrator can do that.")
            if tourney.is_closable():
                tourney.payout()
                messages.add_message(self.request, messages.SUCCESS, "Tournament paid out.")
                return redirect("payout-tournament", tourney_uuid)
            else:
                messages.add_message(self.request, messages.ERROR, "There are still open propositions.")
                return redirect("tournament-details", tourney_uuid)
        
        # We should never get here.
        raise Htpp404

class AddProposition(View):
    """
    This view handles the adding of a proposition into a tournament. It should
    ensure that only the admin can interact with it.
    """
    template_name = "wagers/propositions/add.html"
    def get(self, request, tourney_uuid):
        tourney = Tournament.objects.get(uuid=tourney_uuid)
        # Make sure that the user has admin rights for this tourney.
        if not tourney.is_user_admin(request.user):
            return HttpResponseForbidden("Only the tournament administrator can do that.")
        if not tourney.is_open:
            return HttpResponseForbidden("This tournament is closed.")
        add_prop_form = PropositionForm(initial={"tournament":tourney.id})
        user_is_admin = True
        return render(self.request,
                      self.template_name,
                      {"tourney": tourney,
                       "add_prop_form": add_prop_form,
                       "user_is_admin": user_is_admin})
                       
    def post(self, request, tourney_uuid):
        """
        Tries to add a proposition to the tournament.
        """
        tourney = Tournament.objects.get(uuid=tourney_uuid)
        # Make sure that the user has admin rights for this tourney.
        if not tourney.is_user_admin(request.user):
            return HttpResponseForbidden("Only the tournament administrator can do that.")
        if not tourney.is_open:
            return HttpResponseForbidden("This tournament is closed.")
        form = PropositionForm(request.POST)
        if form.is_valid():
            # Make sure the input wasn't a lie.
            tourney2 = form.get_tournament()
            if not tourney == tourney2:
                return HttpResponseForbidden("Only the tournament administrator can do that.")
            form.save(commit=True)
            return redirect("tournament-details", tourney.uuid)
        else:
            user_is_admin = True
            return render(self.request, 
                          self.template_name, 
                          {"tourney": tourney,
                           "add_prop_form": form,
                           "user_is_admin": user_is_admin})

class OpenProposition(View):
    """
    This view is used to open a prop if the user has the ability to open it. Props shouldn't be
    openable if they have already been paid out.
    """ 
    def post(self, request, tourney_uuid, prop_id):
        print request.POST
        admin_form = PropositionAdminForm(request.POST)
        if admin_form.is_valid(request.user):
            prop = admin_form.get_proposition()
            if prop.is_paid:
                messages.add_message(self.request, messages.ERROR, "This proposition has already been paid out. It cannot be re-opened.")
            else:
                prop.is_open = True
                prop.save()
                messages.add_message(self.request, messages.SUCCESS, "Proposition opened.")
            return redirect("tournament-details", tourney_uuid)
        else:
            return HttpResponseForbidden("You can't do that.")

class CloseProposition(View):
    """
    This view is used to close a prop if the user has the ability to open it.
    """
    def post(self, request, tourney_uuid, prop_id):
        admin_form = PropositionAdminForm(request.POST)
        if admin_form.is_valid(request.user):
            prop = admin_form.get_proposition()
            prop.is_open = False
            prop.save()
            messages.add_message(self.request, messages.SUCCESS, "Proposition closed.")
            return redirect("tournament-details", tourney_uuid)
        else:
            return HttpResponseForbidden("You can't do that.")

class MakeBet(View):
    """
    These views allow users to bet on propositions. Only logged in users should
    be able to access them. Moreover, it should be impossible to make a bet
    unless the user is already a player in a tournament.
    """
    template_name = "wagers/propositions/bet.html"
    def get(self, request, tourney_uuid, prop_id):
        # Only users should be able to get here.
        tourney = Tournament.objects.get(uuid=tourney_uuid)

        prop = Proposition.objects.get(id=prop_id, tournament=tourney)
        form = BetForm(initial={"credits": 1.0, "proposition": prop})
        return render(self.request,
                      self.template_name,
                      {"form": form})
    
    def post(self, request, tourney_uuid, prop_id):
        """
        A currently logged in user who is participating in the tournament can use
        this view to make a bet on an open proposition that they have not yet bet
        on.
        """
        bet_form = BetForm(request.POST)
        tourney = Tournament.objects.get(uuid=tourney_uuid)
        prop = Proposition.objects.get(id=prop_id, tournament=tourney)
        if bet_form.is_valid():
            form_prop = bet_form.cleaned_data["proposition"]
            if prop != form_prop:
                return HttpResponseForbidden("Illegal bet form.")
            player = bet_form.cleaned_data["created_by"]
            if not player.is_user_player(request.user):
                return HttpResponseForbidden("Player and user differ.")
            bet = bet_form.save(commit=False)
            prop.make_bet(bet)
            messages.add_message(self.request, messages.SUCCESS, "Bet made.")
            return redirect("tournament-details", tourney.uuid)
        else:
            return render(self.request, self.template_name, {"form": bet_form})
            
class PayoutProposition(View):
    template_name = "wagers/propositions/pay.html"
    def get(self, request, tourney_uuid, prop_id):
        tourney = Tournament.objects.get(uuid=tourney_uuid)
        prop = Proposition.objects.get(tournament=tourney.id, id=prop_id)
        # Make sure that the user has admin rights for this tourney.
        if not tourney.is_user_admin(request.user):
            return HttpResponseForbidden("Only the tournament administrator can do that.")
        form = PropositionPayoutForm(instance=prop)
        bet_info = prop.get_payout_information()
        return render(self.request, self.template_name, {"form": form,
                                                         "tourney": tourney,
                                                         "prop": prop,
                                                         "bet_info": bet_info})         
    
    def post(self, request, tourney_uuid, prop_id):
        tourney = Tournament.objects.get(uuid=tourney_uuid)
        prop = Proposition.objects.get(tournament=tourney.id, id=prop_id)
        # Make sure that the user has admin rights for this tourney.
        if not tourney.is_user_admin(request.user):
            return HttpResponseForbidden("Only the tournament administrator can do that.")
        form = PropositionPayoutForm(request.POST, instance=prop)
        if form.is_valid():
            proposition = form.save()
            proposition.payout()
            messages.add_message(self.request, messages.SUCCESS, "Proposition paid out.")
            return redirect("payout-proposition", tourney_uuid, prop_id)
        else:
            bet_info = prop.get_payout_information()
            return render(self.request, self.template_name, {"form": form,
                                                             "tourney": tourney,
                                                             "prop": prop,
                                                             "bet_info": bet_info})


