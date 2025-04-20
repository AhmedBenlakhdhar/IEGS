# mgc_project/settings.py

import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# --- Core Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
LOCALE_PATHS = [ BASE_DIR / 'locale', ]

# --- Security Settings ---
# WARNING: Generate a new, strong key for production and load from environment variables.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-droa#jdqf!u^t9t0$ux!_cconx3=bpx=n3a1!dwr*_=50-=51n') # Default for dev

# WARNING: Set DEBUG to False in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true' # Default to True for dev

# WARNING: Restrict ALLOWED_HOSTS in production!
# Example: ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
ALLOWED_HOSTS = ['pixeladder.pythonanywhere.com', '127.0.0.1', 'localhost']

# --- Application Definition ---
INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_recaptcha',
    'widget_tweaks',
    'ckeditor',
    'ckeditor_uploader',
    'compressor',
    'django_countries',
    'ratings.apps.RatingsConfig',
    'articles.apps.ArticlesConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
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

# --- Database ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- Password Validation ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# --- Internationalization (i18n) & Localization (L10n) ---
LANGUAGE_CODE = 'en'
LANGUAGES = [ ('en', _('English')), ('ar', _('Arabic')), ]
MODELTRANSLATION_DEFAULT_LANGUAGE = LANGUAGE_CODE
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- Static files (CSS, JavaScript, Images) ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [ BASE_DIR / 'static', ]
STATIC_ROOT = BASE_DIR / 'staticfiles_collected'
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --- Media files (User Uploads) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Default primary key field type ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Authentication ---
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'login' # Added for clarity, points to the name of your login URL

# --- Google reCAPTCHA (django-recaptcha) ---
RECAPTCHA_PUBLIC_KEY = '6LexugcrAAAAACDHcXQogzALwIC87hxMufE8WAcU'
# Load Secret Key from environment variable, use the one you provided as default for dev
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', '6LexugcrAAAAAJnJge1mqszLJ9B7wATMRyi5KqcJ')

# --- Django Compressor ---
COMPRESS_ENABLED = not DEBUG
COMPRESS_OFFLINE = False
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# --- Email Settings ---
# Configure for actual sending (e.g., using Gmail - REQUIRES App Password if 2FA enabled)
if DEBUG:
    # Use console for local development output
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Use SMTP for production (PythonAnywhere, etc.)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com') # Example for Gmail
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_USE_SSL = False # Typically False if using TLS on port 587
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER') # e.g., 'your_sending_email@gmail.com'
    # *** LOAD PASSWORD FROM ENVIRONMENT VARIABLE ***
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD') # Your App Password or email password
    # Set the default 'From' address
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'MGC Contact <noreply@yourdomain.com>')
    # Set the address for server error emails (often same as DEFAULT_FROM_EMAIL)
    SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)

# --- Admin Emails & Contact Form Recipient ---
# Using Option 1: ADMINS receives both site errors and contact form submissions
ADMINS = [('Ahmed Benlakhdhar', 'ahmedbenlakhdhar@gmail.com')]
MANAGERS = ADMINS

# --- CKEditor Settings ---
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Table', 'HorizontalRule', 'SpecialChar'],
            '/',
            ['Format', 'FontSize'],
            ['TextColor', 'BGColor'],
            ['Maximize', 'ShowBlocks'],
            ['Source'],
        ],
        'height': 300,
        'width': '100%',
        'filebrowserUploadUrl': "/ckeditor/upload/",
        'filebrowserBrowseUrl': "/ckeditor/browse/",
        'allowedContent': True,
        'extraPlugins': 'justify,showblocks,autogrow',
        'autoGrow_minHeight': 250,
        'autoGrow_maxHeight': 600,
        'autoGrow_onStartup': True,
        'contentsCss': [os.path.join(STATIC_URL, 'css/custom.css')],
    },
}

# --- GitHub Webhook ---
GITHUB_WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET', 'YOUR_GITHUB_SECRET_HERE_FOR_DEV_ONLY')
REPO_PATH = os.environ.get('REPO_PATH', '/home/pixeladder/MGC') # Adjusted for your username

# --- django-countries settings (Optional) ---
# COUNTRIES_FLAG_URL = 'flags/{code}.png' # Example

# --- Logging Configuration (Example - uncomment and configure for production) ---
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': 'WARNING',
#             'class': 'logging.FileHandler',
#             'filename': BASE_DIR / 'django_warning.log', # Log warnings/errors
#         },
#         'console': {
#             'level': 'DEBUG' if DEBUG else 'INFO',
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console', 'file'], # Log to both console and file
#             'level': 'INFO',
#             'propagate': True,
#         },
#         'ratings': { # Example: logging for your app
#              'handlers': ['console', 'file'],
#              'level': 'DEBUG' if DEBUG else 'INFO',
#              'propagate': False,
#         },
#     },
# }