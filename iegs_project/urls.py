# iegs_project/urls.py
from django.contrib import admin
from django.urls import path, include
from ratings import views as rating_views # Import ratings views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Games app URLs are now nested under /games/
    path('games/', include('ratings.urls')),
    # Articles app URLs nested under /articles/
    path('articles/', include('articles.urls')),
    # --- NEW: Root URL points to the homepage view ---
    path('', rating_views.homepage, name='home'),
]