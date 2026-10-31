"""Localized text value object with deterministic fallback.

Holds Arabic and English values for bilingual master data and resolves
the appropriate value for a requested locale.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LocalizedText:
    """Bilingual text with fallback.

    Attributes:
        ar: Arabic value.
        en: English value.
    """

    ar: str
    en: str

    def resolve(self, locale: str) -> str:
        """Return the value for ``locale``, falling back to the other language.

        Arabic locales (starting with ``ar``) prefer the Arabic value;
        all other locales prefer English. If the preferred value is empty,
        the other language's value is used.
        """
        value = self.ar if locale.startswith("ar") else self.en
        if value.strip():
            return value
        return self.en if locale.startswith("ar") else self.ar
