from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model

from apps.accounts.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)
from apps.accounts.permissions import IsLibrarianOrReadOnly

User = get_user_model()


class UserListView(generics.ListAPIView):
    """
    GET /users/
    List all users. Librarians can see all, members see limited info.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Non-librarians can only see active users."""
        queryset = super().get_queryset()
        if not self.request.user.is_librarian:
            queryset = queryset.filter(is_active=True)
        return queryset


class UserCreateView(generics.CreateAPIView):
    """
    POST /users/register/
    Public user registration endpoint.
    New users default to MEMBER role.
    """

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """Ensure new users are members by default unless creating user is librarian."""
        if not self.request.user.is_authenticated or not self.request.user.is_librarian:
            # Force MEMBER role for public registrations
            serializer.save(role=User.Role.MEMBER)
        else:
            serializer.save()


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE /users/<id>/
    Users can view/update their own profile.
    Librarians can manage any user.
    """

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        """Users can only access their own profile unless they're librarians."""
        queryset = super().get_queryset()
        if not self.request.user.is_librarian:
            queryset = queryset.filter(id=self.request.user.id)
        return queryset


class CurrentUserView(APIView):
    """
    GET /users/me/
    Get current authenticated user's profile.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """
    POST /users/change-password/
    Allow authenticated users to change their password.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Password updated successfully."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
