"""
URL configuration for loans app.

Design Philosophy:
- POST /loans/checkout/ creates a new Loan (REST resource creation)
- POST /loans/:id/return/ performs return action on existing Loan
- GET /loans/ lists loans (filtered by user role)
- GET /loans/fines/ shows user's fine status
"""

from django.urls import path
from apps.loans import views

app_name = 'loans'

urlpatterns = [
    path('', views.LoanListView.as_view(), name='loan-list'),
    path('checkout/', views.LoanCreateView.as_view(), name='loan-create'),
    path('<int:pk>/', views.LoanDetailView.as_view(), name='loan-detail'),
    path('<int:pk>/return/', views.LoanReturnView.as_view(), name='loan-return'),
    path('fines/', views.UserFineView.as_view(), name='user-fines'),
]
