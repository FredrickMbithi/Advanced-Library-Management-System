"""
core/models.py - State Management (Database/Persistence)

This module defines the Django models that persist library data.
Models handle the database representation while the logic classes
in core/logic/ handle business rules.

Models:
- LibraryItem: Base model for all library items
- Transaction: Tracks checkouts, returns, and fines
- UserProfile: Extended user information for library members
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class LibraryItem(models.Model):
    """
    Database model for library items.
    
    This model stores the persistent state of all library items.
    The business logic for item behavior is in core/logic/items.py.
    """
    
    ITEM_TYPE_CHOICES = [
        ('book', 'Book'),
        ('dvd', 'DVD'),
        ('magazine', 'Magazine'),
        ('ebook', 'EBook'),
        ('audiobook', 'AudioBook'),
    ]
    
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    year_published = models.IntegerField()
    genre = models.CharField(max_length=100)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    
    # Physical item fields
    location = models.CharField(max_length=100, blank=True, default="General Section")
    is_available = models.BooleanField(default=True)
    
    # Digital item fields
    is_digital = models.BooleanField(default=False)
    file_format = models.CharField(max_length=20, blank=True)
    file_size_mb = models.FloatField(default=0.0)
    concurrent_access_limit = models.IntegerField(default=1)
    
    # Book-specific fields
    isbn = models.CharField(max_length=20, blank=True)
    pages = models.IntegerField(default=0)
    edition = models.CharField(max_length=50, blank=True)
    
    # DVD-specific fields
    runtime_minutes = models.IntegerField(default=0)
    rating = models.CharField(max_length=10, blank=True)
    director = models.CharField(max_length=255, blank=True)
    
    # Magazine-specific fields
    issue_number = models.CharField(max_length=50, blank=True)
    issue_date = models.CharField(max_length=50, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    
    # EBook-specific fields
    drm_protected = models.BooleanField(default=True)
    
    # AudioBook-specific fields
    narrator = models.CharField(max_length=255, blank=True)
    duration_hours = models.FloatField(default=0.0)
    chapters = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['item_type']),
            models.Index(fields=['is_available']),
            models.Index(fields=['isbn']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_item_type_display()})"
    
    def get_loan_period_days(self) -> int:
        """Return the loan period based on item type."""
        loan_periods = {
            'book': 14,
            'dvd': 7,
            'magazine': 7,
            'ebook': 21,
            'audiobook': 14,
        }
        return loan_periods.get(self.item_type, 14)
    
    def to_logic_object(self):
        """
        Convert the database model to a logic class instance.
        
        This bridges the persistence layer with the business logic layer.
        """
        from core.logic.items import create_item_from_dict
        
        return create_item_from_dict({
            'item_id': self.id,
            'item_type': self.item_type,
            'title': self.title,
            'author': self.author,
            'year_published': self.year_published,
            'genre': self.genre,
            'location': self.location,
            'isbn': self.isbn,
            'pages': self.pages,
            'edition': self.edition,
            'runtime_minutes': self.runtime_minutes,
            'rating': self.rating,
            'director': self.director,
            'issue_number': self.issue_number,
            'issue_date': self.issue_date,
            'publisher': self.publisher,
            'file_format': self.file_format,
            'file_size_mb': self.file_size_mb,
            'concurrent_access_limit': self.concurrent_access_limit,
            'drm_protected': self.drm_protected,
            'narrator': self.narrator,
            'duration_hours': self.duration_hours,
            'chapters': self.chapters,
        })


class Transaction(models.Model):
    """
    Tracks item checkouts, returns, and associated fines.
    
    Each transaction represents a single checkout event,
    linking a user to a library item with date tracking.
    """
    
    STATUS_CHOICES = [
        ('checked_out', 'Checked Out'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='library_transactions'
    )
    library_item = models.ForeignKey(
        LibraryItem,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    checkout_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='checked_out'
    )
    
    # Fine tracking
    fine_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    fine_paid = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-checkout_date']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['library_item', 'status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.library_item.title} ({self.status})"
    
    def is_overdue(self) -> bool:
        """Check if this transaction is overdue."""
        if self.return_date:
            return False
        return timezone.now() > self.due_date
    
    def calculate_fine(self) -> Decimal:
        """Calculate the current fine using the FineCalculator."""
        from core.logic.calculator import FineCalculator
        calculator = FineCalculator()
        return calculator.calculate_transaction_fine(self)
    
    def save(self, *args, **kwargs):
        """Override save to update status and fine amount."""
        # Update status based on return and due dates
        if self.return_date:
            self.status = 'returned'
        elif self.is_overdue():
            self.status = 'overdue'
        
        # Calculate and store fine amount
        if self.due_date:
            self.fine_amount = self.calculate_fine()
        
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """
    Extended profile for library users.
    
    Stores additional information beyond Django's built-in User model.
    """
    
    MEMBERSHIP_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('student', 'Student'),
        ('senior', 'Senior'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='library_profile'
    )
    
    membership_type = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_CHOICES,
        default='basic'
    )
    membership_start = models.DateField(auto_now_add=True)
    membership_expiry = models.DateField(null=True, blank=True)
    
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Borrowing limits based on membership
    max_items_allowed = models.IntegerField(default=5)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Library Profile"
    
    def get_current_checkouts_count(self) -> int:
        """Get the number of items currently checked out."""
        return Transaction.objects.filter(
            user=self.user,
            status='checked_out'
        ).count()
    
    def can_checkout_more(self) -> bool:
        """Check if user can checkout more items."""
        return self.get_current_checkouts_count() < self.max_items_allowed
    
    def get_total_unpaid_fines(self) -> Decimal:
        """Get total unpaid fines for this user."""
        from core.logic.calculator import FineCalculator
        calculator = FineCalculator()
        return calculator.get_user_total_fines(self.user.id)
