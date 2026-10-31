"""App configuration for the Fatura bounded context."""

from django.apps import AppConfig


class FaturaConfig(AppConfig):
    """Configuration for the fatura Django application.

    This app owns the entire bounded context: domain, application,
    infrastructure, and presentation layers live beneath it.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "fatura"
    verbose_name = "Fatura"

    def ready(self):
        """Register signals and other startup behaviour."""
        import fatura.infrastructure.tasks  # noqa: F401
