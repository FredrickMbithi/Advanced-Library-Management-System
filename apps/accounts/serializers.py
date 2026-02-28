from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer for read operations.
    Exposes safe fields only — no password hash.
    """

    is_librarian = serializers.BooleanField(read_only=True)
    is_member = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_librarian",
            "is_member",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined", "is_librarian", "is_member"]


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles password hashing correctly.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        min_length=8,
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "role",
        ]
        extra_kwargs = {
            "email": {"required": True},
        }

    def validate(self, attrs):
        """Ensure passwords match."""
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        """Create user with properly hashed password."""
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, password=password)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    Password changes should go through a separate endpoint.
    """

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change endpoint."""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        """Verify old password is correct."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        """Ensure new passwords match."""
        if attrs.get("new_password") != attrs.get("new_password_confirm"):
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs

    def save(self, **kwargs):
        """Update the user's password."""
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
