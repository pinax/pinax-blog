import django

DATABASE_ENGINE = "sqlite3"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = [
    "django.contrib.sessions",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.comments",
    "biblion",
]

ROOT_URLCONF = "tests.urls"

SITE_ID = 1

SECRET_KEY = "secret-sauce"

if django.VERSION[:2] < (1, 6):
    TEST_RUNNER = "discover_runner.DiscoverRunner"

ROOT_URLCONF = "tests.urls"

STATIC_URL = "/site_media/static/"
