import os
import sys
from pathlib import Path

from decouple import Csv, config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parents[2]  # /src
ROOT_DIR = BASE_DIR.parent  # /


SECRET_KEY = config(
    "SECRET_KEY", default="dev-secret-key-change-in-production"
)

CONFIGURATION = config("CONFIGURATION", default="dev")
if "test" in sys.argv:
    CONFIGURATION = "testing"

DEBUG = config("DEBUG", default=CONFIGURATION == "dev", cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", default="*" if CONFIGURATION == "dev" else "", cast=Csv()
)
INTERNAL_IPS = config("INTERNAL_IPS", default="127.0.0.1", cast=Csv())

SITE_URL = config("SITE_URL", default="http://localhost:8000")

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS", default=SITE_URL, cast=Csv()
)


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "corsheaders",
    "django_extensions",
    # Project apps
    "frontend",
    "core",
    "accounts",
    "checklist",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "config" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

MIGRATION_MODULES = {
    "checklist": "checklist.infrastructure.migrations",
}

AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = []


# Internationalization

LANGUAGE_CODE = config("LANGUAGE_CODE", default="en-us")

LANGUAGES = [
    ("en", "English"),
]

TIME_ZONE = config("TIME_ZONE", default="UTC")

USE_I18N = True

USE_L10N = True

USE_TZ = True

WSGI_APPLICATION = "config.wsgi.application"

# Static files (CSS, JavaScript, Images)

STATIC_URL = "/static/"
STATIC_ROOT = config(
    "STATIC_ROOT", default=os.path.join(ROOT_DIR, "staticfiles")
)

STATICFILES_DIRS = (os.path.join(BASE_DIR, "config", "static"),)

# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configure REST framework
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "EXCEPTION_HANDLER": "core.exception_handler.exception_handler",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Smartsheet Checklist API",
    "DESCRIPTION": "API for Client Onboarding Checklist backed by Smartsheet",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Authorization header using the Bearer scheme.",
        }
    },
}

CORS_ALLOW_ALL_ORIGINS = True

# JWT settings
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

VITE_DEV_SERVER_HOST = os.environ.get("VITE_DEV_SERVER_HOST", "localhost")


# Encryption key for sensitive fields (must be exactly 32 characters)
DB_ENCRYPTION_KEY = config(
    "DB_ENCRYPTION_KEY", default="change-this-key-in-production!!"
)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
    },
}
