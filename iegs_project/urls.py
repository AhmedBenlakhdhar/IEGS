# iegs_project/urls.py

from django.contrib import admin
from django.urls import path, include
from ratings import views as rating_views # Import views from the 'ratings' app

urlpatterns = [
    # Django Admin Site URL
    path('admin/', admin.site.urls),

    # URLs specific to the 'ratings' app (games, glossary, etc.)
    # All URLs within 'ratings.urls' will be prefixed with '/games/'
    path('games/', include('ratings.urls')),

    # URLs specific to the 'articles' app
    # All URLs within 'articles.urls' will be prefixed with '/articles/'
    path('articles/', include('articles.urls')),

    # --- Authentication URLs ---
    # Include Django's built-in authentication URLs (login, logout, password reset, etc.)
    # These will typically be accessed under '/accounts/' (e.g., /accounts/login/)
    path('accounts/', include('django.contrib.auth.urls')),

    # --- Custom Signup URL ---
    # Map the '/accounts/signup/' URL to our custom signup view
    path('accounts/signup/', rating_views.signup, name='signup'),

    # --- Homepage URL ---
    # The root URL ('/') maps to the homepage view in the 'ratings' app
    path('', rating_views.homepage, name='home'),
]