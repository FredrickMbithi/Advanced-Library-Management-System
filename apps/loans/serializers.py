from rest_framework import serializers
from django.utils import timezone
from apps.loans.models import Loan
from apps.catalog.serializers import PolymorphicLibraryItemSerializer


class LoanSerializer(serializers.ModelSerializer):
    """
    Loan read serializer.
    fine_amount is computed — never writable.
    item is nested read representation.
    """

    item = PolymorphicLibraryItemSerializer(read_only=True)
    borrower_username = serializers.CharField(source="borrower.username", read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    fine_amount = serializers.DecimalField(
        source="fine_preview",
        max_digits=8,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Loan
        fields = [
            "id", "item", "borrower_username",
            "borrowed_at", "due_at", "returned_at",
            "is_active", "is_overdue", "days_overdue", "fine_amount",
        ]
        read_only_fields = fields  # Loans created via service, not direct POST


class LoanCreateSerializer(serializers.Serializer):
    """
    Write serializer for checkout.
    Thin input validation only — business logic in LoanService.checkout().

    Why not ModelSerializer?
    - LoanService controls field population (due_at, borrowed_at).
    - We don't want users setting those fields directly.
    """

    item_id = serializers.IntegerField()

    def validate_item_id(self, value):
        from apps.catalog.models import LibraryItem
        try:
            LibraryItem.objects.get(pk=value)
        except LibraryItem.DoesNotExist:
            raise serializers.ValidationError(f"Item with id={value} does not exist.")
        return value


class ReturnSerializer(serializers.Serializer):
    """
    Minimal serializer for return action.
    loan_id comes from URL kwarg — just needs confirmation payload.
    """
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError("Must confirm return with confirm=true.")
        return value
