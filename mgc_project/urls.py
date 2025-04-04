# mgc_project/urls.py (snippet)
from django.contrib import admin
from django.urls import path, include # Ensure include is imported
from ratings import views as rating_views
from . import views as project_views
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('webhook-trigger-a7b3c9d/', project_views.github_webhook, name='github_webhook'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', rating_views.signup, name='signup'),
    path('i18n/', include('django.conf.urls.i18n')),
    # --- ADD CKEDITOR URLS ---
    path('ckeditor/', include('ckeditor_uploader.urls')),
    # -------------------------
]

urlpatterns += i18n_patterns(
    path('games/', include('ratings.urls')),
    path('articles/', include('articles.urls')),
    path('', rating_views.homepage, name='home'),
    prefix_default_language=True
)

# --- ADD MEDIA URLS FOR DEVELOPMENT ONLY ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ------------------------------------------
