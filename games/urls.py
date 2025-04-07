from django.urls import path
from .views import game_home, poll, map_guess_view, results_view, evaluate_responses, evaluate_user, logout_view, tempo_view, all_responses, view_user_responses, evaluate_response

urlpatterns = [
    path('', game_home, name='game_home'),
    path('poll/', poll, name='poll'),
    path('map_guess/', map_guess_view, name='map_guess'),
    path('results/', results_view, name='results'),
    path('tempo/', tempo_view, name='tempo'),
    path('evaluate/', evaluate_responses, name='evaluate_responses'),
    path('evaluate/<int:user_id>/', evaluate_user, name='evaluate_user'),
    path('evaluate-response/<int:user_id>/', evaluate_response, name='evaluate_response'),
    path('logout/', logout_view, name='logout'),
    path('all-responses/', all_responses, name='all_responses'),
    path('view-responses/<int:user_id>/', view_user_responses, name='view_user_responses'),
]