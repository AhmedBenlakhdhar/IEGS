# articles/urls.py
from django.urls import path
from . import views

app_name = 'articles' # Define the namespace for this app

urlpatterns = [
    # e.g., /articles/
    path('', views.article_list, name='article_list'),
    # --- NEW: Filter by category ---
    path('category/<slug:category_slug>/', views.article_list, name='article_list_by_category'),
    # -------------------------------
    # e.g., /articles/why-mgc-is-important/
    path('<slug:article_slug>/', views.article_detail, name='article_detail'),
]