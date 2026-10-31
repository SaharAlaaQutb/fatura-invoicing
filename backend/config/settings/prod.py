"""Production settings.

Security hardening for deployment behind HTTPS. All secrets come from
environment variables.
"""

from .base import *  # noqa: F401, F403

DEBUG = False

# Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# CORS restricted to configured origins.
CORS_ALLOW_ALL_ORIGINS = False
