"""
core/serializers.py - Data Validation & Transformation

Serializers handle the conversion between Python objects and JSON,
as well as input validation for the API endpoints.

Serializers:
- LibraryItemSerializer: For library item CRUD operations
- TransactionSerializer: For checkout/return operations
- UserProfileSerializer: For user profile management
- CheckoutSerializer: Input validation for checkout requests
- ReturnSerializer: Input validation for return requests
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .models import LibraryItem, Transaction, UserProfile
from .logic.calculator import FineCalculator


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the Django User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class LibraryItemSerializer(serializers.ModelSerializer):
    """
    Serializer for LibraryItem model.
    
    Handles both input validation and output formatting for library items.
    """
    
    loan_period_days = serializers.SerializerMethodField()
    item_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = LibraryItem
        fields = [
            'id', 'title', 'author', 'year_published', 'genre',
            'item_type', 'item_type_display', 'loan_period_days',
            'location', 'is_available', 'is_digital',
            # Book fields
            'isbn', 'pages', 'edition',
            # DVD fields
            'runtime_minutes', 'rating', 'director',
            # Magazine fields
            'issue_number', 'issue_date', 'publisher',
            # Digital fields
            'file_format', 'file_size_mb', 'concurrent_access_limit',
            # EBook fields
            'drm_protected',
            # AudioBook fields
            'narrator', 'duration_hours', 'chapters',
            # Metadata
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_loan_period_days(self, obj) -> int:
        return obj.get_loan_period_days()
    
    def get_item_type_display(self, obj) -> str:
        return obj.get_item_type_display()
    
    def validate_year_published(self, value):
        """Ensure year is reasonable."""
        current_year = timezone.now().year
        if value < 1000 or value > current_year + 1:
            raise serializers.ValidationError(
                f"Year must be between 1000 and {current_year + 1}"
            )
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        item_type = data.get('item_type', '')
        
        # Set is_digital based on item type
        if item_type in ['ebook', 'audiobook']:
            data['is_digital'] = True
        else:
            data['is_digital'] = False
        
        return data


class LibraryItemListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing library items.
    
    Used for list views to reduce payload size.
    """
    
    class Meta:
        model = LibraryItem
        fields = [
            'id', 'title', 'author', 'year_published', 'genre',
            'item_type', 'is_available', 'is_digital',
        ]


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model.
    
    Includes computed fields for fine information.
    """
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    item_title = serializers.CharField(source='library_item.title', read_only=True)
    calculated_fine = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'user_username', 'library_item', 'item_title',
            'checkout_date', 'due_date', 'return_date',
            'status', 'fine_amount', 'fine_paid',
            'calculated_fine', 'is_overdue', 'days_until_due',
            'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'checkout_date', 'fine_amount', 
            'created_at', 'updated_at'
        ]
    
    def get_calculated_fine(self, obj) -> str:
        return str(obj.calculate_fine())
    
    def get_is_overdue(self, obj) -> bool:
        return obj.is_overdue()
    
    def get_days_until_due(self, obj) -> int:
        if obj.return_date:
            return 0
        delta = obj.due_date - timezone.now()
        return delta.days


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""
    
    user = UserSerializer(read_only=True)
    current_checkouts = serializers.SerializerMethodField()
    total_unpaid_fines = serializers.SerializerMethodField()
    can_checkout = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'membership_type', 'membership_start',
            'membership_expiry', 'phone', 'address', 'max_items_allowed',
            'current_checkouts', 'total_unpaid_fines', 'can_checkout',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_current_checkouts(self, obj) -> int:
        return obj.get_current_checkouts_count()
    
    def get_total_unpaid_fines(self, obj) -> str:
        return str(obj.get_total_unpaid_fines())
    
    def get_can_checkout(self, obj) -> bool:
        calculator = FineCalculator()
        can_checkout, _ = calculator.can_user_checkout(obj.user.id)
        return can_checkout and obj.can_checkout_more()


class CheckoutRequestSerializer(serializers.Serializer):
    """
    Serializer for checkout request validation.
    
    Validates the input for a checkout operation and performs
    business rule validation.
    """
    
    user_id = serializers.IntegerField()
    item_id = serializers.IntegerField()
    custom_due_date = serializers.DateTimeField(required=False, allow_null=True)
    
    def validate_user_id(self, value):
        """Validate user exists and can checkout."""
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        
        # Check if user can checkout
        calculator = FineCalculator()
        can_checkout, reason = calculator.can_user_checkout(value)
        if not can_checkout:
            raise serializers.ValidationError(reason)
        
        return value
    
    def validate_item_id(self, value):
        """Validate item exists and is available."""
        try:
            item = LibraryItem.objects.get(id=value)
        except LibraryItem.DoesNotExist:
            raise serializers.ValidationError("Item not found")
        
        # Physical items must be available
        if not item.is_digital and not item.is_available:
            raise serializers.ValidationError("Item is not available for checkout")
        
        return value
    
    def validate_custom_due_date(self, value):
        """Validate custom due date is in the future."""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Due date must be in the future")
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        user_id = data.get('user_id')
        
        # Check if user has reached checkout limit
        try:
            profile = UserProfile.objects.get(user_id=user_id)
            if not profile.can_checkout_more():
                raise serializers.ValidationError({
                    'user_id': f"User has reached maximum checkout limit "
                              f"({profile.max_items_allowed} items)"
                })
        except UserProfile.DoesNotExist:
            # No profile exists, allow checkout with default limits
            pass
        
        return data


class ReturnRequestSerializer(serializers.Serializer):
    """
    Serializer for return request validation.
    
    Validates the input for a return operation.
    """
    
    transaction_id = serializers.IntegerField(required=False)
    user_id = serializers.IntegerField(required=False)
    item_id = serializers.IntegerField(required=False)
    return_date = serializers.DateTimeField(required=False, allow_null=True)
    
    def validate(self, data):
        """Ensure we can identify the transaction."""
        transaction_id = data.get('transaction_id')
        user_id = data.get('user_id')
        item_id = data.get('item_id')
        
        if not transaction_id and not (user_id and item_id):
            raise serializers.ValidationError(
                "Either transaction_id or both user_id and item_id must be provided"
            )
        
        # Find the transaction
        if transaction_id:
            try:
                transaction = Transaction.objects.get(id=transaction_id)
            except Transaction.DoesNotExist:
                raise serializers.ValidationError({
                    'transaction_id': "Transaction not found"
                })
        else:
            try:
                transaction = Transaction.objects.get(
                    user_id=user_id,
                    library_item_id=item_id,
                    status='checked_out'
                )
            except Transaction.DoesNotExist:
                raise serializers.ValidationError(
                    "No active checkout found for this user and item"
                )
        
        if transaction.status == 'returned':
            raise serializers.ValidationError("Item has already been returned")
        
        data['transaction'] = transaction
        return data


class FinePaymentSerializer(serializers.Serializer):
    """Serializer for fine payment validation."""
    
    transaction_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    def validate_amount(self, value):
        """Ensure payment amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be positive")
        return value
    
    def validate_transaction_id(self, value):
        """Validate transaction exists."""
        try:
            Transaction.objects.get(id=value)
        except Transaction.DoesNotExist:
            raise serializers.ValidationError("Transaction not found")
        return value
