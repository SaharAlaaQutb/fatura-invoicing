"""Test settings.

Fast password hashers, in-memory SQLite, eager Celery, and console
mailer keep the test suite quick and hermetic.
"""

from .base import *  # noqa: F401, F403

DEBUG = False

DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///:memory:"),
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
