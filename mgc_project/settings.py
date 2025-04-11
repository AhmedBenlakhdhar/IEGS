# mgc_project/settings.py

import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Use your actual secret key here
SECRET_KEY = 'django-insecure-droa#jdqf!u^t9t0$ux!_cconx3=bpx=n3a1!dwr*_=50-=51n'

# GITHUB WEBHOOK CONFIGURATION
# !!! CHANGE THIS TO A STRONG, RANDOM SECRET !!!
GITHUB_WEBHOOK_SECRET = 'M@a=pUN-8W}J6*E?Y;D{()' # Must match GitHub
# Path to the root of your git repository on PythonAnywhere
# BASE_DIR usually points to the directory containing manage.py, which is often the repo root. Adjust if needed.

REPO_PATH = '/home/pixeladder/MGC'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True # Keep True for development, SET TO FALSE FOR PRODUCTION

ALLOWED_HOSTS = [
    'pixeladder.pythonanywhere.com', # Your live domain
    '127.0.0.1',                   # Keep for local if needed
    'localhost',                   # Keep for local if needed
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
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Add whitenoise if not using PA static files mapping
    'django.contrib.sessions.middleware.SessionMiddleware',
    # --- LocaleMiddleware (After Session, Before Common) ---
    'django.middleware.locale.LocaleMiddleware',
    # ---------------------------------------------------------
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
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Or BASE_DIR / 'templates'
        'APP_DIRS': True, # This should normally find the tags
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # --- ADD context processor for languages ---
                'django.template.context_processors.i18n',
                # ------------------------------------------
            ],
        },
    },
]

WSGI_APPLICATION = 'mgc_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization (i18n) & Localization (L10n)
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en' # Default language code (e.g., 'en', 'en-us')

# --- Define available languages ---
LANGUAGES = [
    ('en', _('English')),
    ('ar', _('Arabic')),
]
# --------------------------------

# --- Set path for translation files ---
LOCALE_PATHS = [
    BASE_DIR / 'locale', # Creates locale/ folder at project root
]
# ------------------------------------

# --- Modeltranslation settings ---
MODELTRANSLATION_DEFAULT_LANGUAGE = LANGUAGE_CODE
# Optional: specify languages explicitly if different from LANGUAGES
# MODELTRANSLATION_LANGUAGES = ('en', 'ar')
# Optional: configure fallback behavior
# MODELTRANSLATION_FALLBACK_LANGUAGES = {'default': ('en',)} # Default behavior is usually good
# --------------------------------

TIME_ZONE = 'UTC'

USE_I18N = True # --- Ensure Internationalization is Enabled ---

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/' # URL prefix for static files
STATICFILES_DIRS = [ BASE_DIR / 'static', ] # For YOUR app's static files during development

# --- CORRECTED STATIC_ROOT ---
# This is where `collectstatic` will copy ALL static files (yours + admin + others)
STATIC_ROOT = BASE_DIR / 'staticfiles_collected'
# -----------------------------

# Optional: If using WhiteNoise (simpler setup sometimes)
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media' # Creates media/ folder at project root

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Auth Redirect URLs ---
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
# LOGIN_URL = '/accounts/login/' # Default is usually fine
# --------------------------

# Add these lines anywhere in settings.py
RECAPTCHA_PUBLIC_KEY = '6LexugcrAAAAACDHcXQogzALwIC87hxMufE8WAcU'  # Paste your Site Key
RECAPTCHA_PRIVATE_KEY = '6LexugcrAAAAAJnJge1mqszLJ9B7wATMRyi5KqcJ' # Paste your Secret Key

# Set to True in production (usually based on DEBUG setting)
COMPRESS_ENABLED = not DEBUG # Enable compression when DEBUG is False
# Set to True if you want to pre-compress files during deployment using `manage.py compress`
COMPRESS_OFFLINE = False

# --- Compressor STATICFILES_FINDERS ---
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
# -------------------------------------------

# --- Email Backend Configuration (REQUIRED for Contact Form) ---
# For development, use the console backend:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production, configure your actual email provider (e.g., Gmail, SendGrid)
# See: https://docs.djangoproject.com/en/5.0/topics/email/#smtp-backend
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.example.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@example.com'
# EMAIL_HOST_PASSWORD = 'your-email-password-or-app-password'
# DEFAULT_FROM_EMAIL = 'MGC Contact <noreply@yourdomain.com>' # Email shown as sender
# SERVER_EMAIL = DEFAULT_FROM_EMAIL # Email for server errors

# --- CKEDITOR CONFIGURATION ---
CKEDITOR_UPLOAD_PATH = "uploads/" # Subdirectory within MEDIA_ROOT
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar': 'Custom', # Use a custom toolbar defined below
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Strike', '-', 'TextColor', 'BGColor'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Table', 'HorizontalRule', 'SpecialChar'],
            ['Format', 'FontSize'], # Keep format for Headings
            ['Source'], # Allow viewing HTML source
            '/', # Line break
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['RemoveFormat'],
            ['Maximize', 'ShowBlocks'],
            # Add PasteFromWord, PasteText if needed
        ],
        'height': 300,
        'width': '100%', # Make it responsive
        'filebrowserUploadUrl': "/ckeditor/upload/", # Make sure this matches urls.py
        'filebrowserBrowseUrl': "/ckeditor/browse/", # Requires configuration if you want server-side browsing
         # --- Configure language based on Django's language ---
        # 'language': '{{ language }}', # This syntax might require template processing context not available here.
                                     # CKEditor usually picks up the browser language or you can set it explicitly.
                                     # For multi-language admin, CKEditor integration with modeltranslation handles it.
         # --- Allow specific HTML content ---
        'allowedContent': True,
        'extraPlugins': 'justify,showblocks,autogrow',
         'autoGrow_minHeight': 250,
         'autoGrow_maxHeight': 600,
         'autoGrow_onStartup': True,
         'contentsCss': [os.path.join(STATIC_URL, 'css/custom.css')],
    },
    'articles_toolbar': { # Example of a different toolbar for articles if needed
         'toolbar': 'Basic',
         'height': 200,
         # Inherits other settings from 'default' unless overridden
    }
}
