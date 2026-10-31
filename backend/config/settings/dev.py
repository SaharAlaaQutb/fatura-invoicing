"""Development settings.

Debug mode enabled, console email backend, permissive CORS for local
frontend development.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "backend"]

CORS_ALLOW_ALL_ORIGINS = True

# Use console mailer in development so emails print to stdout.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Celery runs eagerly in dev for simpler debugging.
CELERY_TASK_ALWAYS_EAGER = True

# Allow insecure HTTP for local development.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
