"""Celery application configuration for the Fatura project."""

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("fatura")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
