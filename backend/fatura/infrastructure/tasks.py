"""Celery task entrypoints for the Fatura bounded context.

Tasks here are thin wrappers: they resolve the use case from the
composition root and delegate business logic to it. No business rules
live in tasks.
"""

from celery import shared_task


@shared_task(bind=True)
def debug_task(self):
    """Debug task for verifying Celery wiring."""
    print(f"Request: {self.request!r}")
