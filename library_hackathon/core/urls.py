"""
core/urls.py - API Routing

Maps URL patterns to views for the library management API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LibraryItemViewSet,
    TransactionViewSet,
    UserProfileViewSet,
    CheckoutView,
    ReturnView,
    FineView,
    FinePaymentView,
    OverdueReportView,
    health_check,
)

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'items', LibraryItemViewSet, basename='libraryitem')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'users', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    # Health check
    path('health/', health_check, name='health-check'),
    
    # Checkout and return operations
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('return/', ReturnView.as_view(), name='return'),
    
    # Fine management
    path('fines/', FineView.as_view(), name='fines'),
    path('fines/pay/', FinePaymentView.as_view(), name='fine-payment'),
    path('fines/report/', OverdueReportView.as_view(), name='overdue-report'),
    
    # Include router URLs
    path('', include(router.urls)),
]
