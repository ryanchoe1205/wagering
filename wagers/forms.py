from django import forms
from django.shortcuts import get_object_or_404
from models import Tournament

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

                        