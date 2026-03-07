"""
Django settings for shotsbybeysos project.
"""

from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────
# SECURITY — change SECRET_KEY before deploying
# ─────────────────────────────────────────────
SECRET_KEY = 'django-insecure-change-this-before-production-use'

DEBUG = True  # Set to False in production

ALLOWED_HOSTS = ['*']  # Restrict in production e.g. ['shotsbybeysos.com', 'www.shotsbybeysos.com']

# ─────────────────────────────────────────────
# STRIPE CONFIGURATION
# ─────────────────────────────────────────────
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_REPLACE_WITH_YOUR_STRIPE_KEY')
STRIPE_SECRET_KEY      = os.environ.get('STRIPE_SECRET_KEY',      'sk_test_REPLACE_WITH_YOUR_STRIPE_SECRET')
STRIPE_WEBHOOK_SECRET  = os.environ.get('STRIPE_WEBHOOK_SECRET',  '')

# Price per photo in cents (2500 = $25.00)
PRICE_PER_PHOTO = 2500
CURRENCY        = 'usd'

# ─────────────────────────────────────────────
# EMAIL CONFIGURATION
# Using Django's built-in email backend.
# For production, swap to SMTP or a service like SendGrid / Mailgun.
# ─────────────────────────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.console.EmailBackend'  # prints to console during dev
# EMAIL_BACKEND     = 'django.core.mail.backends.smtp.EmailBackend'     # uncomment for production
EMAIL_HOST          = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@shotsbybeysos.com')
STUDIO_EMAIL        = os.environ.get('STUDIO_EMAIL', 'hello@shotsbybeysos.com')  # receives order notifications

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'shotsbybeysos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
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

WSGI_APPLICATION = 'shotsbybeysos.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (uploaded photos)
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
