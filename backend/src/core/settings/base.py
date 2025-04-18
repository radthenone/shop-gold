import os
from datetime import timedelta

from core.paths import SRC_DIR

DJANGO_LOCAL = os.environ.get("DJANGO_LOCAL", "1") == "1"

# Frontend integration
FRONTEND_HOST = os.environ.get("FRONTEND_HOST", "localhost")
FRONTEND_PORT = os.environ.get("FRONTEND_PORT", "8080")
FRONTEND_URL = os.environ.get("FRONTEND_URL", f"http://{FRONTEND_HOST}:{FRONTEND_PORT}")

# Core Django Settings
SECRET_KEY = str(os.environ.get("DJANGO_SECRET_KEY", "secret_key"))
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = list(
    str(os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")).split(",")
)
ALLOWED_HOSTS += list(os.environ.get("ALLOWED_HOSTS", "").split(","))

# Application definition
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "django_celery_beat",
    "storages",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "allauth",
    # "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "channels",
]

LOCAL_APPS = [
    "apps.users",
    "apps.payments",
    "apps.orders",
    "apps.shop",
    "apps.delivery",
    "apps.files",
    "apps.notifications",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "kolo.middleware.KoloMiddleware",
    # "allauth.account.middleware.AccountMiddleware",
    "core.middleware.TOTPMiddleware",
]

# Basic Django config
ROOT_URLCONF = "core.urls"
AUTH_USER_MODEL = "users.User"
SITE_ID = 1
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [SRC_DIR / "templates"],
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

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("POSTGRES_DB", "postgres"),
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": int(os.environ.get("POSTGRES_PORT", "5433")),
    }
}

# Password validation
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Warsaw"
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "1025"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "0") == "1"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@example.com")

# Django AllAuth settings
ACCOUNT_ADAPTER = "core.adapters.AccountAdapter"
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]


ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_VERIFICATION_BY_CODE = True
EMAIL_EXPIRE_DAYS = timedelta(minutes=15).total_seconds() / (24 * 60 * 60)
ACCOUNT_EMAIL_VERIFICATION_EXPIRE_DAYS = EMAIL_EXPIRE_DAYS  # 15 minutes

ACCOUNT_EMAIL_SUBJECT_PREFIX = ""
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = "/"
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "/"
ACCOUNT_EMAIL_CONFIRMATION_HMAC = True

# Django AllAuth mfa settings
MFA_ADAPTER = "core.adapters.MFAAdapter"
TOTP_DIGITS = 6
TOTP_PERIOD = 30
TOTP_ISSUER = "Your App Name"
MFA_METHODS = {
    "totp": {
        "name": "TOTP (Time-based One-Time Password)",
        "validator": "allauth.mfa.totp.validator.TOTPValidator",
    },
    "recovery": {
        "name": "Recovery Codes",
        "validator": "allauth.mfa.recovery.validator.RecoveryCodeValidator",
    },
}

# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS512",
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    FRONTEND_URL,
]
CORS_ALLOW_CREDENTIALS = True
