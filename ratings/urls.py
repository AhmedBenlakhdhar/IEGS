# ratings/urls.py
from django.urls import path
from . import views

app_name = 'ratings' # Define the namespace

urlpatterns = [
    # Game list views
    path('', views.game_list, name='game_list'),
    path('developer/<slug:developer_slug>/', views.game_list, name='games_by_developer'),
    path('publisher/<slug:publisher_slug>/', views.game_list, name='games_by_publisher'),

    # Glossary & Info Pages
    path('glossary/', views.glossary_view, name='glossary'),
    path('methodology/', views.methodology_view, name='methodology'),
    path('why-mgc/', views.why_mgc_view, name='why_mgc'),
    path('contact/', views.contact_view, name='contact'),
    path('contact/success/', views.contact_success_view, name='contact_success'),

    # Discussion Comment actions (Keep these)
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/flag/', views.flag_comment, name='flag_comment'),

    # --- REMOVE User Contribution Action URLs ---
    # path('contribution/<int:contribution_id>/delete/', views.delete_contribution, name='delete_contribution'),
    # path('contribution/<int:contribution_id>/flag/', views.flag_contribution, name='flag_contribution'),

    # --- ADD Suggestion Action URLs (Optional - Primarily for Admin/Staff Use) ---
    # These might not be directly linked from the frontend unless you add buttons.
    path('suggestion/<int:suggestion_id>/delete/', views.delete_suggestion, name='delete_suggestion'),
    # path('suggestion/<int:suggestion_id>/flag/', views.flag_suggestion, name='flag_suggestion'), # Add if needed

    # Game detail (Keep last as it uses a general slug)
    path('<slug:game_slug>/', views.game_detail, name='game_detail'),
]