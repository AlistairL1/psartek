from django.urls import path
from .views import game_home, poll, map_guess_view, results_view, logout_view, all_responses, delete_response

urlpatterns = [
    path('', game_home, name='game_home'),
    path('poll/', poll, name='poll'),
    path('map_guess/', map_guess_view, name='map_guess'),
    path('results/', results_view, name='results'),
    path('logout/', logout_view, name='logout'),
    path('all-responses/', all_responses, name='all_responses'),
    path('delete-response/', delete_response, name='delete_response'),
]