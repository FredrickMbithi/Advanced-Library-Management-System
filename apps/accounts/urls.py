from django.urls import path
from apps.accounts.views import (
    UserListView,
    UserCreateView,
    UserDetailView,
    CurrentUserView,
    ChangePasswordView,
)

app_name = "accounts"

urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/register/", UserCreateView.as_view(), name="user-register"),
    path("users/me/", CurrentUserView.as_view(), name="user-current"),
    path("users/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]
