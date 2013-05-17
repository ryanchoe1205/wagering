from django import forms
from django.shortcuts import get_object_or_404
from models import Tournament
from models import Proposition
from models import Bet

class TournamentForm(forms.Form):
    """
    This form is used to interact with Tournament models.
    """
    uuid = forms.CharField(min_length=32, max_length=32, 
                           widget=forms.HiddenInput)
    
    def get_tournament(self):
        """
        This method should only be called when the form has already been
        cleaned. It tries to return the tournament the form directs to. Otherwise
        returns 404.
        """  
        uuid = self.cleaned_data["uuid"]
        return get_object_or_404(Tournament, uuid=uuid)

class PropositionForm(forms.ModelForm):
    """
    This form is used to create Propositions.
    """
    schedule_toggle = forms.BooleanField(required=False)
    
    class Meta:
        model = Proposition
        exclude = ("outcome")
        widgets = {"tournament": forms.HiddenInput()}
    
    def clean(self):
        cleaned_data = super(PropositionForm, self).clean()
        # If the user didn't want to schedule opening and closing
        if not cleaned_data.get("schedule_toggle"):
            cleaned_data["open_wager_at"] = None
            cleaned_data["close_wager_at"] = None
        return cleaned_data
        
        
        
    def get_tournament(self):
        """
        This method should only be called when the form has already been
        cleaned. It tries to return the tournament the form directs to.
        """
        return self.cleaned_data["tournament"]

class BetForm(forms.ModelForm):
    """
    This form is used to create bets.
    """
    class Meta:
        model = Bet
        widgets = {"proposition": forms.HiddenInput(), 
                   "credits": forms.HiddenInput(),
                   "created_by": forms.HiddenInput()}
                   
    def clean(self):
        cleaned_data = super(BetForm, self).clean()
        proposition = cleaned_data.get("proposition")
        if not proposition.is_open_for_betting():
            raise forms.ValidationError("The proposition is not open for betting.")
        
        player = cleaned_data.get("created_by")
        if not proposition.can_player_bet(player):
            raise forms.ValidationError("You can't make a bet on this proposition.")
        
        credits = cleaned_data.get("credits")
        if not player.can_afford_bet(credits):
            raise forms.ValidationError("Not enough credits.")
            
        return cleaned_data

class PropositionPayoutForm(forms.ModelForm):
    class Meta:
        model = Proposition
        fields = ["tournament", "outcome"]
        widgets = {"tournament": forms.HiddenInput()}
        
class PropositionAdminForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput)
        
    def is_valid(self, user):
        valid = super(PropositionAdminForm, self).is_valid()
        if valid:
            prop = self.get_proposition()
            if prop.tournament.is_user_admin(user):
                return valid
        return False
                    
    def get_proposition(self):
        """
        This method should only be called when the form has already been
        cleaned. It tries to return the proposition the form directs to. Otherwise
        returns 404.
        """
        id = self.cleaned_data.get("id")
        return get_object_or_404(Proposition, id=id)
                  
        

class ScheduleForm(forms.Form):
    start_time = forms.DateTimeField()
    end_time = forms.DateTimeField()
    MLB = forms.BooleanField(required=False)
    NBA = forms.BooleanField(required=False)
    NFL = forms.BooleanField(required=False)
    NHL = forms.BooleanField(required=False)
    UFC = forms.BooleanField(required=False)
    MLS = forms.BooleanField(required=False)

class GameDatabaseForm(forms.Form):
    selected = forms.BooleanField(required=False)
    id = forms.IntegerField(widget=forms.HiddenInput)
    team_a = forms.CharField(required=False)
    team_b = forms.CharField(required=False)
