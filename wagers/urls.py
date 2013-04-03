from wagers.views import WagerView, WagerPayoutView, WagerDeleteView, WagerCreateView, ResetEverythingView
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required
from django.views.generic.list import ListView
from wagers.models import Wager
from django.contrib.auth.models import User

class WagerListView(ListView):
    model = Wager


class UserListView(ListView):
    model = User



#url(r'^wagers/delete/', WagerDeleteView.as_view())
urlpatterns = patterns('',
    url(r'^wagers/tourneyreset', permission_required("wagers.delete_wager")(ResetEverythingView.as_view())),
    url(r'^wagers/index/', WagerListView.as_view(), name="wager-list"),
    url(r'^wagers/delete/', permission_required("wagers.delete_wager")(WagerDeleteView.as_view())),
    url(r'^wagers/add/', permission_required("wagers.add_wager")(WagerCreateView.as_view())),
    url(r'^wagers/payout/', permission_required("wagers.change_wager")(WagerPayoutView.as_view())),
    url(r'^wagers', WagerView.as_view(template_name="wagers/wager.html")),
    url(r'^leaderboard/', UserListView.as_view(), name="player-list"))
