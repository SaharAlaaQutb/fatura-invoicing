"""Locale resolution middleware.

Sets the active Django translation language from the authenticated
user's ``preferred_language``, falling back to ``Accept-Language`` and
then ``DEFAULT_LOCALE``. Runs after AuthenticationMiddleware so
``request.user`` is available.
"""

from django.utils import translation

from django.conf import settings


class LocaleMiddleware:
    """Middleware that activates the request's locale."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        locale = self._resolve_locale(request)
        translation.activate(locale)
        request.LANGUAGE_CODE = translation.get_language()
        response = self.get_response(request)
        translation.deactivate()
        return response

    def _resolve_locale(self, request):
        """Resolve the locale for the current request."""
        # 1. Authenticated user's preferred language.
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            return getattr(user, "preferred_language", None) or settings.DEFAULT_LOCALE

        # 2. Accept-Language header.
        accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
        if accept_language:
            first = accept_language.split(",")[0].split(";")[0].strip()[:2]
            if first in dict(settings.LANGUAGES) if hasattr(settings, "LANGUAGES") else []:
                return first

        # 3. Default locale.
        return settings.DEFAULT_LOCALE
