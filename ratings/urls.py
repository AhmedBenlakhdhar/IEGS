# ratings/urls.py
from django.urls import path
from . import views

app_name = 'ratings' # Define the namespace

urlpatterns = [
    # Game list views
    path('', views.game_list, name='game_list'),
    path('developer/<slug:developer_slug>/', views.game_list, name='games_by_developer'),
    path('publisher/<slug:publisher_slug>/', views.game_list, name='games_by_publisher'),

    path('methodology/', views.methodology_view, name='methodology'),
    path('why-mgc/', views.why_mgc_view, name='why_mgc'),
    path('contact/', views.contact_view, name='contact'),
    path('contact/success/', views.contact_success_view, name='contact_success'),

    # User Profile URL
    path('profile/', views.user_profile_edit, name='profile_edit'),

    # Comment actions
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/flag/', views.flag_comment, name='flag_comment'),

    # Suggestion Actions (Optional)
    path('suggestion/<int:suggestion_id>/delete/', views.delete_suggestion, name='delete_suggestion'),

    # Game detail (Keep last)
    path('<slug:game_slug>/', views.game_detail, name='game_detail'),
]