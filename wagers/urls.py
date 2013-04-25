from wagers.views import AddTournament
from wagers.views import OpenTournamentList
from wagers.views import ActiveTournamentList
from wagers.views import TournamentDetails
from wagers.views import JoinTournament
from wagers.views import PayoutTournament
from wagers.views import AddProposition
from wagers.views import OpenProposition
from wagers.views import CloseProposition
from wagers.views import PayoutProposition
from wagers.views import MakeBet
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required, login_required

urlpatterns = patterns('',
    url(r'^tournaments/([a-f0-9]{32})$', TournamentDetails.as_view(), name="tournament-details"),
    url(r'^tournaments/public/', OpenTournamentList.as_view(), name="open-tournament-list"),
    url(r'^tournaments/active/', ActiveTournamentList.as_view(), name="active-tournament-list"),
    url(r'^tournaments/join/', JoinTournament.as_view(), name="join-tournament"),
    url(r'^tournaments/add/$', login_required(AddTournament.as_view()), name="add-tournament"),
    url(r'^tournaments/([a-f0-9]{32})/pay/$', login_required(PayoutTournament.as_view()), name="payout-tournament"),
    url(r'^tournaments/([a-f0-9]{32})/props/add/$', login_required(AddProposition.as_view()), name="add-proposition"),
    url(r'^tournaments/([a-f0-9]{32})/props/(\d+)/bet/$', login_required(MakeBet.as_view()), name="make-bet"),
    url(r'^tournaments/([a-f0-9]{32})/props/(\d+)/pay/$', login_required(PayoutProposition.as_view()), name="payout-proposition"),
    url(r'^tournaments/([a-f0-9]{32})/props/(\d+)/open/$', login_required(OpenProposition.as_view()), name="open-proposition"),
    url(r'^tournaments/([a-f0-9]{32})/props/(\d+)/close/$', login_required(CloseProposition.as_view()), name="close-proposition"))
