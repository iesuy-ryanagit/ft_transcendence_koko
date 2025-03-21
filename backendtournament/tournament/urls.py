from django.urls import path
from tournament.views import (
    CreateTournamenView,
    JoinTournamentView,
    MatchEndView,
    TournamentListView,
    TournamentDetailView,
    TournamentFinishView,
    TournamentStartView,
    JoinTournamentParticipantView,
    TournamentResultDetailView,
    TournamentResultListView
)
urlpatterns = [
    path('tournament/create/', CreateTournamenView.as_view(), name='tournament_create'),
    path('tournament/join/', JoinTournamentParticipantView.as_view(), name='tournament_join'),
    path('tournament/match/end/', MatchEndView.as_view(), name='match_end'),
    path('tournament/list/', TournamentListView.as_view(), name='tournament_list'),
    path('tournament/<uuid:pk>/', TournamentDetailView.as_view(), name='tournament_detail'),
    path('tournament/finish/', TournamentFinishView.as_view(), name='tournament_finish'),
    path('tournament/start/', TournamentStartView.as_view(), name='tournament_start'),
    path('tournament/result/', TournamentResultListView.as_view(), name='tournament_result_list'),
    path('tournament/result/<uuid:id>/', TournamentResultDetailView.as_view(), name='tournament_result_detail'),
]