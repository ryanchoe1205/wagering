from wagers.views import AddTournament
from wagers.views import OpenTournamentList
from wagers.views import UserTournamentList
from wagers.views import TournamentDetails
from wagers.views import TournamentAdmin
from wagers.views import ShareTournament
from wagers.views import JoinTournament
from wagers.views import PayoutTournament
from wagers.views import AddProposition
from wagers.views import AddPropositionFromDatabase
from wagers.views import OpenProposition
from wagers.views import CloseProposition
from wagers.views import PayoutProposition
from wagers.views import MakeBet
from wagers.views import BetHistoryView
from wagers.views import ChangeSchedule
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required, login_required

urlpatterns = patterns('',
    url(r'^history/$', login_required(BetHistoryView.as_view()), name='bet-history'),
    url(r'^tournaments/([a-f0-9]{32})$', TournamentDetails.as_view(), name="tournament-details"),
    url(r'^tournaments/([a-f0-9]{32})/admin/$', TournamentAdmin.as_view(), name="tournament-admin"),
    url(r'^tournaments/([a-f0-9]{32})/share/$', login_required(ShareTournament.as_view()), name="share-tournament"),
    url(r'^tournaments/public/', OpenTournamentList.as_view(), name="open-tournament-list"),
    url(r'^tournaments/$', UserTournamentList.as_view(), name="user-tournament-list"),
    url(r'^tournaments/join/', JoinTournament.as_view(), name="join-tournament"),
    url(r'^tournaments/add/$', login_required(AddTournament.as_view()), name="add-tournament"),
    url(r'^tournaments/([a-f0-9]{32})/pay/$', login_required(PayoutTournament.as_view()), name="payout-tournament"),
    url(r'^tournaments/([a-f0-9]{32})/props/add/$', login_required(AddProposition.as_view()), name="add-proposition"),
    url(r'^tournaments/([a-f0-9]{32})/props/add-selected/$', login_required(AddPropositionFromDatabase.as_view()), name="add-selected"),
    url(r'^tournaments/([a-f0-9]{32})/props/(\d+)/bet/$', login_required(MakeBet.as_view()), name="make-bet"),
    url(r'^tournaments/([a-f0-9]{32})/props/(\d+)/schedule/$', login_required(ChangeSchedule.as_view()), name="change-schedule"),
    url(r'^tournaments/([a-f0-9]{32})/props/(\d+)/pay/$', login_required(PayoutProposition.as_view()), name="payout-proposition"),
    url(r'^tournaments/([a-f0-9]{32})/props/(\d+)/open/$', login_required(OpenProposition.as_view()), name="open-proposition"),
    url(r'^tournaments/([a-f0-9]{32})/props/(\d+)/close/$', login_required(CloseProposition.as_view()), name="close-proposition"))