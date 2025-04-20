# mgc_project/settings.py

import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# --- Core Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
LOCALE_PATHS = [ BASE_DIR / 'locale', ] # Moved near BASE_DIR for clarity

# --- Security Settings ---
# WARNING: Keep the secret key used in production secret!
# Generate a new, strong key for production and load from environment variables.
# DO NOT use the reCAPTCHA key here. The default insecure key is fine for DEVELOPMENT ONLY.
SECRET_KEY = 'django-insecure-droa#jdqf!u^t9t0$ux!_cconx3=bpx=n3a1!dwr*_=50-=51n'

# WARNING: Set DEBUG to False in production!
DEBUG = True

# WARNING: Restrict ALLOWED_HOSTS in production to only your domain(s)!
ALLOWED_HOSTS = [
    'pixeladder.pythonanywhere.com', # Example production host
    '127.0.0.1',
    'localhost',
]

# --- Application Definition ---
INSTALLED_APPS = [
    'modeltranslation', # Should generally be before admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'django_recaptcha',
    'widget_tweaks',
    'ckeditor',
    'ckeditor_uploader',
    'compressor',
    'django_countries',

    # Your apps
    'ratings.apps.RatingsConfig',
    'articles.apps.ArticlesConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Correct placement for WhiteNoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', # Correct placement for i18n
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
                'django.template.context_processors.i18n', # Essential for language switching
            ],
        },
    },
]

WSGI_APPLICATION = 'mgc_project.wsgi.application'

# --- Database ---
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# WARNING: Use a more robust database like PostgreSQL for production.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- Password Validation ---
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# --- Internationalization (i18n) & Localization (L10n) ---
# https://docs.djangoproject.com/en/5.1/topics/i18n/
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', _('English')),
    ('ar', _('Arabic')),
]
MODELTRANSLATION_DEFAULT_LANGUAGE = LANGUAGE_CODE # For django-modeltranslation
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True # Recommended for timezone handling

# --- Static files (CSS, JavaScript, Images) ---
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = 'static/'
STATICFILES_DIRS = [ BASE_DIR / 'static', ] # Your project's static files
# WARNING: Ensure STATIC_ROOT is configured correctly for your deployment environment (e.g., PythonAnywhere)
STATIC_ROOT = BASE_DIR / 'staticfiles_collected' # Directory for collectstatic
# For WhiteNoise (serving static files in production)
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --- Media files (User Uploads) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media' # Where user uploads will be stored

# --- Default primary key field type ---
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Authentication ---
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# --- Google reCAPTCHA (django-recaptcha) ---
# You get these keys from https://www.google.com/recaptcha/admin/
RECAPTCHA_PUBLIC_KEY = '6LexugcrAAAAACDHcXQogzALwIC87hxMufE8WAcU'
# WARNING: Load RECAPTCHA_PRIVATE_KEY from environment variable in production!
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY', '6LexugcrAAAAAJnJge1mqszLJ9B7wATMRyi5KqcJ') # Use env var or default for dev

# --- Django Compressor ---
# Enable compression only when DEBUG is False (production)
COMPRESS_ENABLED = not DEBUG
COMPRESS_OFFLINE = False # Set to True if you want to pre-compress during deployment
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder', # Compressor finder
)

# --- Email Settings ---
# WARNING: Use console backend for development ONLY. Configure SMTP for production.
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # PRODUCTION EMAIL SETTINGS (Replace placeholders and use environment variables for password)
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.example.com') # E.g., 'smtp.gmail.com', 'mail.privateemail.com'
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587)) # 587 for TLS, 465 for SSL
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true' # Use TLS (recommended)
    EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() == 'true' # Set to True ONLY if your provider uses port 465
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your_email@example.com') # Your full email address
    # *** LOAD PASSWORD FROM ENVIRONMENT VARIABLE ***
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD') # Your email password or app-specific password
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'MGC Contact <noreply@yourdomain.com>') # Sender address users see
    SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL) # Address Django sends error emails from

# --- Admin Emails ---
# Replace with your actual name and email for site error notifications
ADMINS = [('Your Name', 'your_admin_email@example.com')]
MANAGERS = ADMINS # Typically the same as ADMINS

# --- CKEditor Settings (django-ckeditor) ---
CKEDITOR_UPLOAD_PATH = "uploads/" # Ensure MEDIA_ROOT is correctly set for this
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa', # Uses the standard Moono Lisa skin
        'toolbar': 'Custom', # Use the custom toolbar definition below
        'toolbar_Custom': [
            # Define your desired toolbar layout here
            ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Table', 'HorizontalRule', 'SpecialChar'],
            '/', # Line break
            ['Format', 'FontSize'], # Keep Format and Font Size
            ['TextColor', 'BGColor'],
            ['Maximize', 'ShowBlocks'],
            ['Source'], # Keep Source button
            # Add other buttons as needed, remove unwanted ones
        ],
        'height': 300,
        'width': '100%',
        'filebrowserUploadUrl': "/ckeditor/upload/", # Make sure this URL is correctly configured in urls.py
        'filebrowserBrowseUrl': "/ckeditor/browse/", # Make sure this URL is correctly configured in urls.py
        'allowedContent': True, # Be cautious with this in production if you don't trust all content creators
        'extraPlugins': 'justify,showblocks,autogrow', # Standard extra plugins
        'autoGrow_minHeight': 250,
        'autoGrow_maxHeight': 600,
        'autoGrow_onStartup': True,
        'contentsCss': [os.path.join(STATIC_URL, 'css/custom.css')], # Link to your site's CSS if needed
    },
}

# --- GitHub Webhook ---
# WARNING: Load GITHUB_WEBHOOK_SECRET from environment variable in production!
GITHUB_WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET', 'M@a=pUN-8W}J6*E?Y;D{()_DEV_ONLY')
# WARNING: Ensure REPO_PATH is correct for your deployment environment
REPO_PATH = os.environ.get('REPO_PATH', '/path/to/your/repo/on/server') # Example path, adjust as needed

# --- django-countries settings (Optional) ---
# COUNTRIES_FLAG_URL = 'flags/{code}.gif' # Example if using custom flags path within static
# COUNTRIES_ONLY = ['US', 'GB', ...] # Restrict countries if needed
# COUNTRIES_FIRST = ['US']

# --- Logging Configuration (Optional but recommended for production) ---
# Example basic logging setup:
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': 'WARNING', # Log warnings and errors to a file in production
#             'class': 'logging.FileHandler',
#             'filename': BASE_DIR / 'django_debug.log',
#         },
#         'console': {
#             'level': 'INFO', # Log info level to console in development
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file' if not DEBUG else 'console'],
#             'level': 'INFO', # Adjust level as needed
#             'propagate': True,
#         },
#     },
# }

# Ensure this directory exists if logging to file
# if not DEBUG and not os.path.exists(BASE_DIR / 'django_debug.log'):
#     with open(BASE_DIR / 'django_debug.log', 'w') as f:
#         f.write("Log file created.\n")