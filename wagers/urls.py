from wagers.views import WagerView, WagerPayoutView, WagerDeleteView, WagerCreateView, ResetEverythingView, WagerOpenView, WagerCloseView, WagerListView, WagerHistoryView
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required, login_required
from django.views.generic.list import ListView
from wagers.models import Wager
from django.contrib.auth.models import User



class UserListView(ListView):
    model = User



#url(r'^wagers/delete/', WagerDeleteView.as_view())
urlpatterns = patterns('',
    url(r'^wagers/tourneyreset', permission_required("wagers.delete_wager")(ResetEverythingView.as_view())),
    url(r'^wagers/index/', login_required(WagerListView.as_view())),
    url(r'^wagers/history/', login_required(WagerHistoryView.as_view())),
    url(r'^wagers/delete/', permission_required("wagers.delete_wager")(WagerDeleteView.as_view())),
    url(r'^wagers/add/', permission_required("wagers.add_wager")(WagerCreateView.as_view())),
    url(r'^wagers/open/', permission_required("wagers.change_wager")(WagerOpenView.as_view())),
    url(r'^wagers/close/', permission_required("wagers.change_wager")(WagerCloseView.as_view())),
    url(r'^wagers/payout/', permission_required("wagers.change_wager")(WagerPayoutView.as_view())),
    url(r'^wagers', WagerView.as_view(template_name="wagers/wager.html")),
    url(r'^leaderboard/', UserListView.as_view(), name="player-list"))
