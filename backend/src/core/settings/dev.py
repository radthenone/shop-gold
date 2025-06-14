from core.settings.base import *

# Debug settings
DEBUG = True
DJANGO_LOCAL = os.environ.get("DJANGO_LOCAL", "1") == "1"

# Frontend integration
FRONTEND_HOST = os.environ.get("FRONTEND_HOST", "127.0.0.1")
FRONTEND_PORT = os.environ.get("FRONTEND_PORT", "4200")
FRONTEND_URL = os.environ.get("FRONTEND_URL", f"http://{FRONTEND_HOST}:{FRONTEND_PORT}")

# Extend allowed hosts
ALLOWED_HOSTS += list(os.environ.get("ALLOWED_HOSTS", "").split(","))

# Development apps
INSTALLED_APPS += [
    "drf_spectacular",
    "debug_toolbar",
]

# Middleware settings
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

# REST Framework - add schema class for development
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "drf_spectacular.openapi.AutoSchema"

# CORS settings
CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]
CORS_ALLOWED_ORIGINS += (
    list(os.environ.get("CORS_ALLOWED_ORIGINS", "").split(","))
    if os.environ.get("CORS_ALLOWED_ORIGINS")
    else []
)

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "accept-language",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-api-version",
]

# Storage settings
USE_AWS = False
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "minioadmin")
AWS_S3_REGION_NAME = os.environ.get("AWS_REGION", "us-east-1")
AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL", "http://minio:9000")
AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN", "localhost:9000")
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "static")

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = AWS_S3_ENDPOINT_URL
# STATICFILES_STORAGE = "core.storages.StaticStorage"
STORAGES = {
    "staticfiles": {"BACKEND": "core.storages.StaticStorage"},
}
#
# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_true": {"()": "django.utils.log.RequireDebugTrue"}},
    "formatters": {"rich": {"datefmt": "[%X]"}},
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler",
            "filters": ["require_debug_true"],
            "formatter": "rich",
            "level": "DEBUG",
            "rich_tracebacks": True,
            "tracebacks_show_locals": True,
        }
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# API Documentation settings
SPECTACULAR_SETTINGS = {
    "TITLE": "Your API",
    "DESCRIPTION": "Your project description",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_SPLIT_RESPONSE": True,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
    },
}

# Redis Configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_DB = os.environ.get("REDIS_DB", 0)

# Celery Configuration
CELERY_BROKER_URL = os.environ.get(
    "CELERY_BROKER_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
)
CELERY_RESULT_BACKEND = os.environ.get(
    "CELERY_RESULT_BACKEND", f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Warsaw"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"


# Django caches
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Django Channels Configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.pubsub.RedisPubSubChannelLayer",
        "CONFIG": {
            "hosts": [f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"],
            "serializer_format": "json",
        },
    },
}
