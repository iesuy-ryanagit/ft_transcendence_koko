from django.urls import path
from tournament.views import (
    CreateTournamenView,
    JoinTournamentView,
    MatchEndView,
    TournamentListView,
    TournamentDetailView,
    TournamentFinishView,
    TournamentStartView,
    JoinTournamentParticipantView
)
urlpatterns = [
    path('tournament/create/', CreateTournamenView.as_view(), name='tournament_create'),
    path('tournament/join/', JoinTournamentParticipantView.as_view(), name='tournament_join'),
    path('match/end/', MatchEndView.as_view(), name='match_end'),
    path('tournament/list/', TournamentListView.as_view(), name='tournament_list'),
    path('tournament/<uuid:pk>/', TournamentDetailView.as_view(), name='tournament_detail'),
    path('tournament/finish/', TournamentFinishView.as_view(), name='tournament_finish'),
    path('tournament/start/', TournamentStartView.as_view(), name='tournament_start'),
]