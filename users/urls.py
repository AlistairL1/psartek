from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='users_home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
