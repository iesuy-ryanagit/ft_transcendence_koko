from django.urls import path
from tournament.views import CreateTournamenView, RecordScoreView

urlpatterns = [
    path('tournament/create/', CreateTournamenView.as_view(), name='create_tournament'),
    path('scores/record/', RecordScoreView.as_view(), name='record_score'),
]