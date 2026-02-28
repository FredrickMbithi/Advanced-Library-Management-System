"""
Main URL configuration for library_system project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.accounts.urls')),
    path('api/catalog/', include('apps.catalog.urls')),
    path('api/loans/', include('apps.loans.urls')),
]
