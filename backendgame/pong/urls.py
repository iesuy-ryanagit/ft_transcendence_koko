from django.urls import path
from . import views

urlpatterns = [
    path('pong/start/', views.match_start, name='pong_match_start'),
    path('pong/data/', views.match_data, name='pong_match_data'),
]