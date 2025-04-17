# mgc_project/settings.py

import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-droa#jdqf!u^t9t0$ux!_cconx3=bpx=n3a1!dwr*_=50-=51n'
GITHUB_WEBHOOK_SECRET = 'M@a=pUN-8W}J6*E?Y;D{()'
REPO_PATH = '/home/pixeladder/MGC'
DEBUG = True
ALLOWED_HOSTS = [
    'pixeladder.pythonanywhere.com',
    '127.0.0.1',
    'localhost',
]

# Application definition
INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ratings.apps.RatingsConfig',
    'articles.apps.ArticlesConfig',
    'django_recaptcha',
    'widget_tweaks',
    'ckeditor',
    'ckeditor_uploader',
    'compressor',
    'django_countries',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', # LocaleMiddleware correct position
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mgc_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'mgc_project.wsgi.application'

# Database
DATABASES = { 'default': { 'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3', } }

# Password validation
AUTH_PASSWORD_VALIDATORS = [ {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',}, {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',}, {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',}, {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',}, ]

# Internationalization (i18n) & Localization (L10n)
LANGUAGE_CODE = 'en'
LANGUAGES = [ ('en', _('English')), ('ar', _('Arabic')), ]
LOCALE_PATHS = [ BASE_DIR / 'locale', ]
MODELTRANSLATION_DEFAULT_LANGUAGE = LANGUAGE_CODE
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [ BASE_DIR / 'static', ]
STATIC_ROOT = BASE_DIR / 'staticfiles_collected'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Auth Redirect URLs
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# reCAPTCHA
RECAPTCHA_PUBLIC_KEY = '6LexugcrAAAAACDHcXQogzALwIC87hxMufE8WAcU'
RECAPTCHA_PRIVATE_KEY = '********************' # Use your actual secret key

# Compressor
COMPRESS_ENABLED = not DEBUG
COMPRESS_OFFLINE = False
STATICFILES_FINDERS = ( 'django.contrib.staticfiles.finders.FileSystemFinder', 'django.contrib.staticfiles.finders.AppDirectoriesFinder', 'compressor.finders.CompressorFinder', )

# Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # Development setting
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # Example Production
# EMAIL_HOST = 'smtp.example.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@example.com'
# EMAIL_HOST_PASSWORD = 'your-email-password-or-app-password'
# DEFAULT_FROM_EMAIL = 'MGC Contact <noreply@yourdomain.com>'
# SERVER_EMAIL = DEFAULT_FROM_EMAIL
ADMINS = [('Your Name', 'your_admin_email@example.com')] # ADD YOUR ADMIN EMAIL(S)

# CKEDITOR
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa', 'toolbar': 'Custom',
        'toolbar_Custom': [ ['Bold', 'Italic', 'Underline', 'Strike', '-', 'TextColor', 'BGColor'], ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote'], ['Link', 'Unlink', 'Anchor'], ['Image', 'Table', 'HorizontalRule', 'SpecialChar'], ['Format', 'FontSize'], ['Source'], '/', ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'], ['RemoveFormat'], ['Maximize', 'ShowBlocks'], ],
        'height': 300, 'width': '100%',
        'filebrowserUploadUrl': "/ckeditor/upload/", 'filebrowserBrowseUrl': "/ckeditor/browse/",
        'allowedContent': True, 'extraPlugins': 'justify,showblocks,autogrow',
        'autoGrow_minHeight': 250, 'autoGrow_maxHeight': 600, 'autoGrow_onStartup': True,
        'contentsCss': [os.path.join(STATIC_URL, 'css/custom.css')],
    },
}
