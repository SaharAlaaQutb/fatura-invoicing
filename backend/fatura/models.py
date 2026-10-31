"""Custom user model for the Fatura bounded context.

Defines the application's authentication model. Email is used as the
username field. Each user carries a role (owner / accountant / cashier)
and a preferred language (ar / en) used for localization.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model authenticating by email instead of username.

    Fields:
        email: Unique email address used for login.
        role: Business role determining what the user may do.
        preferred_language: User's UI language (ar / en).
    """

    class Role(models.TextChoices):
        """User roles mapped to the permission matrix."""

        OWNER = "owner", "Owner"
        ACCOUNTANT = "accountant", "Accountant"
        CASHIER = "cashier", "Cashier"

    class Language(models.TextChoices):
        """Supported UI languages."""

        ARABIC = "ar", "Arabic"
        ENGLISH = "en", "English"

    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CASHIER,
        help_text="Determines which actions the user may perform.",
    )
    preferred_language = models.CharField(
        max_length=10,
        choices=Language.choices,
        default=Language.ARABIC,
        help_text="User's preferred UI and document language.",
    )

    # Email-based authentication: username is not used.
    username = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.email
