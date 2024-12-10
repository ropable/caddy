"""
Django settings for caddy project.
"""

import os
import sys

import dj_database_url

from caddy.utils import env

# Project paths
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.join(BASE_DIR, "caddy")
# Add PROJECT_DIR to the system path.
sys.path.insert(0, PROJECT_DIR)

# Application definition
DEBUG = env("DEBUG", False)
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
SECRET_KEY = env("SECRET_KEY", "PlaceholderSecretKey")
CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE", False)
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE", False)
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT", False)
SECURE_REFERRER_POLICY = env("SECURE_REFERRER_POLICY", None)
SECURE_HSTS_SECONDS = env("SECURE_HSTS_SECONDS", 0)
if not DEBUG:
    ALLOWED_HOSTS = env("ALLOWED_DOMAINS", "").split(",")
else:
    ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = ["127.0.0.1", "::1"]
ROOT_URLCONF = "caddy.urls"
WSGI_APPLICATION = "caddy.wsgi.application"

# Azure blob storage credentials.
AZURE_ACCOUNT_NAME = env("AZURE_ACCOUNT_NAME", "account_name")
AZURE_ACCOUNT_KEY = env("AZURE_ACCOUNT_KEY", "account_key")
AZURE_CONTAINER = env("AZURE_CONTAINER", "container")

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.postgres",
    "django_extensions",
    "tastypie",
    "shack",
)
MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(PROJECT_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
            ],
        },
    },
]


# Database configuration
DATABASES = {
    # Defined in the DATABASE_URL env variable.
    "default": dj_database_url.config(),
}


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Australia/Perth"
USE_I18N = False
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# Tastypie settings
TASTYPIE_DEFAULT_FORMATS = ["json", "jsonp"]


# Logging settings
LOGGING = {
    "version": 1,
    "formatters": {
        "verbose": {"format": "%(asctime)s %(levelname)-12s %(name)-12s %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": sys.stdout,
            "level": "WARNING",
        },
        "caddy": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": sys.stdout,
            "level": "INFO",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
        },
        "caddy": {"handlers": ["caddy"], "level": "INFO"},
    },
}
