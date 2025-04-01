# mgc_project/urls.py

from django.contrib import admin
from django.urls import path, include
from ratings import views as rating_views

# --- Import the new webhook view ---
from . import views as project_views # Assuming views.py is in the same dir (mgc_project)

# --- Imports needed for Internationalization ---
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _ # Keep import

# --- URLs NOT prefixed with language ---
urlpatterns = [
    # --- Add the webhook URL here ---
    # Use a hard-to-guess path instead of 'update_server' for slightly better obscurity
    path('webhook-trigger-a7b3c9d/', project_views.github_webhook, name='github_webhook'),
    # --------------------------------

    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', rating_views.signup, name='signup'),
    path('i18n/', include('django.conf.urls.i18n')), # For set_language view
]

# --- URLs THAT WILL BE prefixed with language ---
urlpatterns += i18n_patterns(
    path('games/', include('ratings.urls')),
    path('articles/', include('articles.urls')),
    path('', rating_views.homepage, name='home'),
    prefix_default_language=True
)

# Add this at the end if you use static files during development (PythonAnywhere handles static files differently in production)
# from django.conf import settings
# from django.conf.urls.static import static
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)