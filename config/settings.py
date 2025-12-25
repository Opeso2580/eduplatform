from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # your apps
    "accounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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
        "DIRS": [BASE_DIR / "templates"],  # IMPORTANT
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

WSGI_APPLICATION = "config.wsgi.application"

# ✅ Use your custom user model
AUTH_USER_MODEL = "accounts.CustomUser"

# ✅ Login routing
LOGIN_URL = "student_login"
LOGIN_REDIRECT_URL = "student_dashboard"
LOGOUT_REDIRECT_URL = "student_login"

# Static files
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media (for Profile.avatar ImageField)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "eduplatform_db",
        "USER": "postgres",
        "PASSWORD": "Babarisi@2580",
        "HOST": "localhost",
        "PORT": "5432",
    }
}


DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

SECRET_KEY = "qh%_-owsvbwcq7dwzrd@9l^k8@ni+7ql=e&sl3-u(y)5tuk98!"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@vantagelinguahub.com"


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = "vantagelinguahub20@gmail.com"
EMAIL_HOST_PASSWORD = "cyvbomkmlppaagxb"

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
