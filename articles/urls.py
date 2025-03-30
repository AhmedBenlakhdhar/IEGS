# articles/urls.py
from django.urls import path
from . import views

app_name = 'articles' # Define the namespace for this app

urlpatterns = [
    # e.g., /articles/
    path('', views.article_list, name='article_list'),

    # e.g., /articles/why-iegs-is-important/
    path('<slug:article_slug>/', views.article_detail, name='article_detail'),
]