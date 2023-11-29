from django.urls import path
from . import views

urlpatterns = [
    path('', views.predict_score, name='predict_score'),
    path('players', views.players_performance, name='players_performance'),
    path('players_performance', views.players_performance, name='players_performance'),
    path('team_analysiss', views.team_analysiss, name='team_analysiss'),


]
