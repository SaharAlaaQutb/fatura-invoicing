"""Root URL configuration for the Fatura project."""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("fatura.presentation.api.urls")),
]
