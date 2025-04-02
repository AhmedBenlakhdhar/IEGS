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
DEBUG = True # Keep True for development

ALLOWED_HOSTS = [
    'pixeladder.pythonanywhere.com', # For PythonAnywhere
    '127.0.0.1',                    # For local development (standard IP)
    'localhost',                    # For local development (standard hostname)
]


# Application definition

INSTALLED_APPS = [
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
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # --- ADD LocaleMiddleware (After Session, Before Common) ---
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

LANGUAGE_CODE = 'en-us' # Default language

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

TIME_ZONE = 'UTC'

USE_I18N = True # --- Enable Internationalization ---

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [ BASE_DIR / 'static', ]
STATIC_ROOT = '/home/pixeladder/MGC/venv/Lib/site-packages/django/contrib/staticfiles'


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Auth Redirect URLs ---
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
# LOGIN_URL = '/accounts/login/' # Default is usually fine
# --------------------------

# Add these lines anywhere in settings.py
RECAPTCHA_PUBLIC_KEY = '6LeZpAcrAAAAAChxgWEoMz9JOHkkcE3plMzh6eD_'  # Paste your Site Key
RECAPTCHA_PRIVATE_KEY = '6LeZpAcrAAAAAC9lLdEKjOmUW2jSKc0JnoR2pSfs' # Paste your Secret Key