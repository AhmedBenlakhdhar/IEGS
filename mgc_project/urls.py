# mgc_project/urls.py
from django.contrib import admin
from django.urls import path, include
from ratings import views as rating_views # Ensure this line is correct
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
    path('i18n/', include('django.conf.urls.i18n')), # Language switcher URLs
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

urlpatterns += i18n_patterns(
    path('games/', include('ratings.urls')),
    path('articles/', include('articles.urls')),
    path('', rating_views.homepage, name='home'),
    prefix_default_language=True
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Usually not needed