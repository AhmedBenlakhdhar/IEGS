# articles/urls.py
from django.urls import path
from . import views

app_name = 'articles' # Define the namespace for this app

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('category/<slug:category_slug>/', views.article_list, name='article_list_by_category'),

    # --- NEW: Comment Action URLs ---
    path('comment/<int:comment_id>/delete/', views.delete_article_comment, name='delete_article_comment'),
    path('comment/<int:comment_id>/flag/', views.flag_article_comment, name='flag_article_comment'),
    # ---------------------------------

    # Article detail (Keep last as it uses a general slug)
    path('<slug:article_slug>/', views.article_detail, name='article_detail'),
]