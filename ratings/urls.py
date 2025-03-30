# ratings/urls.py
from django.urls import path
from . import views

app_name = 'ratings'  # Define the namespace for this app

urlpatterns = [
    # e.g., /games/ (Handled by the root path in iegs_project/urls.py if using 'home')
    # If you want a separate /games/ path distinct from home, keep this:
    path('', views.game_list, name='game_list'),

    # e.g., /games/minecraft-survival/
    path('<slug:game_slug>/', views.game_detail, name='game_detail'),
]