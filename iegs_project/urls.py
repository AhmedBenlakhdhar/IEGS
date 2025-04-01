# iegs_project/urls.py (Corrected Version - v3)

from django.contrib import admin
from django.urls import path, include
from ratings import views as rating_views

# --- Imports needed for Internationalization ---
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _ # Keep import

urlpatterns = [
    # URLs NOT prefixed with language
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', rating_views.signup, name='signup'),
    path('i18n/', include('django.conf.urls.i18n')), # For set_language view
]

# URLs THAT WILL BE prefixed with language (/en/, /ar/, etc.)
urlpatterns += i18n_patterns(
    # --- NO _() wrapper around path string when using include() ---
    path('games/', include('ratings.urls')),
    path('articles/', include('articles.urls')),
    # -------------------------------------------------------------

    # Root path for the language
    path('', rating_views.homepage, name='home'),

    # Other paths pointing DIRECTLY to a view can use _() if desired
    # path(_('about-us/'), some_app.views.about, name='about'),

    # Settings for i18n_patterns
    prefix_default_language=True
)