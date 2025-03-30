# ratings/urls.py - FULL FILE
from django.urls import path
from . import views

app_name = 'ratings'

urlpatterns = [
    # Changed game_list to accept optional slugs
    path('', views.game_list, name='game_list'),
    path('developer/<slug:developer_slug>/', views.game_list, name='games_by_developer'),
    path('publisher/<slug:publisher_slug>/', views.game_list, name='games_by_publisher'),
    path('glossary/', views.glossary_view, name='glossary'), # NEW: Glossary page
    path('<slug:game_slug>/', views.game_detail, name='game_detail'), # Keep game detail last
]