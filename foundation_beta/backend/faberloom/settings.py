"""Django settings for FaberLoom Foundation Beta (M16)."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "unsafe-local-key")
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "channels",
    "apps.core",
    "apps.tenants",
    "apps.users",
    "apps.auth_session",
    "apps.events",
    "apps.rbac",
    "apps.audit",
    "apps.policy",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.auth_session.middleware.SessionMiddleware",
    "apps.rbac.middleware.RBACMiddleware",
    "apps.core.middleware.TenantMiddleware",
]

ROOT_URLCONF = "faberloom.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "faberloom.wsgi.application"
ASGI_APPLICATION = "faberloom.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "faberloom"),
        "USER": os.environ.get("POSTGRES_USER", "faberloom_app"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "devpassword"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

if os.environ.get("DATABASE_URL"):
    import dj_database_url

    DATABASES["default"] = dj_database_url.parse(os.environ.get("DATABASE_URL"))

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# Tenant isolation configuration
TENANT_ID_HEADER = "HTTP_X_TENANT_ID"
TENANT_TESTING_HEADER_ALLOWED = DEBUG or os.environ.get("TESTING", "False").lower() == "true"

# Auth session settings
SESSION_COOKIE_NAME = "session_id"
SESSION_TTL_SECONDS = int(os.environ.get("SESSION_TTL_SECONDS", "28800"))
SESSION_REMEMBER_TTL_SECONDS = int(os.environ.get("SESSION_REMEMBER_TTL_SECONDS", "2592000"))
TOTP_ISSUER = os.environ.get("TOTP_ISSUER", "FaberLoom")
TOTP_ENCRYPTION_KEY = os.environ.get("TOTP_ENCRYPTION_KEY", "")
TOTP_ATTEMPTS_LIMIT = int(os.environ.get("TOTP_ATTEMPTS_LIMIT", "3"))
TOTP_LOCKOUT_SECONDS = int(os.environ.get("TOTP_LOCKOUT_SECONDS", "900"))

# RBAC
ACTIVE_HAT_HEADER = "HTTP_X_ACTIVE_HAT"
INVITATION_TTL_DAYS = int(os.environ.get("INVITATION_TTL_DAYS", "7"))

# Channels / WebSocket
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get("REDIS_URL", "redis://localhost:6379/0")],
        },
    },
}

# M15 Outbox Streams
EVENT_STREAM_TTL_SECONDS = int(os.environ.get("EVENT_STREAM_TTL_SECONDS", "86400"))
OUTBOX_RETENTION_DAYS = int(os.environ.get("OUTBOX_RETENTION_DAYS", "7"))

# M12 Audit Trail
AUDIT_EXPORT_FORMAT = os.environ.get("AUDIT_EXPORT_FORMAT", "json,csv")
AUDIT_VALIDATION_HOUR = int(os.environ.get("AUDIT_VALIDATION_HOUR", "2"))

# Celery
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# MinIO / S3 compatible
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "faberloom")
MINIO_SECURE = os.environ.get("MINIO_SECURE", "False").lower() == "true"

# LiteLLM
LITELLM_URL = os.environ.get("LITELLM_URL", "http://localhost:4000")
LITELLM_API_KEY = os.environ.get("LITELLM_API_KEY", "sk-faberloom-local")

# Letta
LETTA_URL = os.environ.get("LETTA_URL", "http://localhost:8283")

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
