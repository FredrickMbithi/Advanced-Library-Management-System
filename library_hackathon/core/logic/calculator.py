"""
core/logic/calculator.py - Encapsulation (Service Layer)

This module encapsulates all fine calculation logic in a single place.
Instead of spreading fine logic across views and models, we centralize
it here for maintainability and testability.

The fine formula is:
    Fine = max(0, (return_date - due_date).days × daily_rate)

Business Rules:
- Fines only accrue for overdue items
- Maximum daily fine rate is $1 per day (configurable)
- Users with fines > $50 are blocked from checkout
- Digital items do not incur fines
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Union, Optional, TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from core.models import Transaction


class FineCalculator:
    """
    Service class for calculating and managing library fines.
    
    This class encapsulates all fine-related business logic,
    making it easy to modify fine policies without changing
    other parts of the application.
    
    Class Attributes:
        DEFAULT_DAILY_RATE: Default fine amount per day overdue
        MAX_FINE_FOR_CHECKOUT: Maximum unpaid fines before blocking checkout
    """
    
    DEFAULT_DAILY_RATE = Decimal('1.00')
    MAX_FINE_FOR_CHECKOUT = Decimal('50.00')
    
    def __init__(
        self,
        daily_rate: Optional[Decimal] = None,
        max_fine_for_checkout: Optional[Decimal] = None
    ):
        """
        Initialize the calculator with configurable rates.
        
        Args:
            daily_rate: Fine per day overdue, defaults to settings or $1
            max_fine_for_checkout: Max unpaid fines to allow checkout
        """
        # Try to get from Django settings, fall back to defaults
        self.daily_rate = daily_rate or Decimal(
            str(getattr(settings, 'FINE_PER_DAY', self.DEFAULT_DAILY_RATE))
        )
        self.max_fine_for_checkout = max_fine_for_checkout or Decimal(
            str(getattr(settings, 'MAX_FINE_BEFORE_CHECKOUT_BLOCKED', 
                       self.MAX_FINE_FOR_CHECKOUT))
        )
    
    def calculate_fine(
        self,
        due_date: Union[datetime, date],
        return_date: Optional[Union[datetime, date]] = None
    ) -> Decimal:
        """
        Calculate the fine for a late return.
        
        Formula: Fine = max(0, (return_date - due_date).days × daily_rate)
        
        Args:
            due_date: When the item was due
            return_date: When the item was returned (defaults to today)
            
        Returns:
            Decimal amount of the fine (0 if not overdue)
        """
        if return_date is None:
            return_date = datetime.now()
        
        # Normalize to date objects for consistent comparison
        if isinstance(due_date, datetime):
            due_date = due_date.date()
        if isinstance(return_date, datetime):
            return_date = return_date.date()
        
        days_overdue = (return_date - due_date).days
        
        if days_overdue <= 0:
            return Decimal('0.00')
        
        fine = Decimal(days_overdue) * self.daily_rate
        return fine.quantize(Decimal('0.01'))
    
    def calculate_transaction_fine(self, transaction: 'Transaction') -> Decimal:
        """
        Calculate the fine for a specific transaction.
        
        Args:
            transaction: The Transaction model instance
            
        Returns:
            Decimal fine amount
        """
        if not transaction.due_date:
            return Decimal('0.00')
        
        return_date = transaction.return_date or datetime.now()
        return self.calculate_fine(transaction.due_date, return_date)
    
    def get_user_total_fines(self, user_id: int) -> Decimal:
        """
        Get the total unpaid fines for a user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Total unpaid fine amount
        """
        # Import here to avoid circular imports
        from core.models import Transaction
        
        unpaid_transactions = Transaction.objects.filter(
            user_id=user_id,
            fine_paid=False,
            return_date__isnull=False
        )
        
        total = Decimal('0.00')
        for transaction in unpaid_transactions:
            total += self.calculate_transaction_fine(transaction)
        
        return total.quantize(Decimal('0.01'))
    
    def can_user_checkout(self, user_id: int) -> tuple[bool, str]:
        """
        Check if a user is allowed to checkout items.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        total_fines = self.get_user_total_fines(user_id)
        
        if total_fines > self.max_fine_for_checkout:
            return (
                False,
                f"Outstanding fines of ${total_fines} exceed the "
                f"${self.max_fine_for_checkout} limit. Payment required before checkout."
            )
        
        return (True, "Account in good standing")
    
    def pay_fine(self, transaction_id: int, amount: Decimal) -> dict:
        """
        Process a fine payment for a transaction.
        
        Args:
            transaction_id: The transaction's ID
            amount: Amount being paid
            
        Returns:
            Dict with payment result details
        """
        from core.models import Transaction
        
        try:
            transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            return {
                'success': False,
                'error': f'Transaction {transaction_id} not found'
            }
        
        fine_amount = self.calculate_transaction_fine(transaction)
        
        if amount < fine_amount:
            return {
                'success': False,
                'error': f'Payment of ${amount} is less than fine of ${fine_amount}'
            }
        
        transaction.fine_paid = True
        transaction.save()
        
        return {
            'success': True,
            'transaction_id': transaction_id,
            'fine_amount': str(fine_amount),
            'amount_paid': str(amount),
            'change': str(amount - fine_amount)
        }


class FineReport:
    """
    Utility class for generating fine reports.
    
    Provides methods to generate summaries of fines for
    administrative purposes.
    """
    
    def __init__(self, calculator: Optional[FineCalculator] = None):
        self.calculator = calculator or FineCalculator()
    
    def get_overdue_items_report(self) -> list[dict]:
        """
        Generate a report of all currently overdue items.
        
        Returns:
            List of dicts with overdue item details
        """
        from core.models import Transaction
        
        today = datetime.now().date()
        overdue_transactions = Transaction.objects.filter(
            return_date__isnull=True,
            due_date__lt=today
        ).select_related('library_item', 'user')
        
        report = []
        for transaction in overdue_transactions:
            fine = self.calculator.calculate_fine(
                transaction.due_date, 
                datetime.now()
            )
            report.append({
                'transaction_id': transaction.id,
                'user_id': transaction.user_id,
                'user_email': transaction.user.email if transaction.user else None,
                'item_id': transaction.library_item_id,
                'item_title': transaction.library_item.title,
                'due_date': transaction.due_date.isoformat(),
                'days_overdue': (today - transaction.due_date.date()).days,
                'current_fine': str(fine),
            })
        
        return report
    
    def get_user_fine_summary(self, user_id: int) -> dict:
        """
        Get a detailed fine summary for a specific user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Dict with user's fine details
        """
        from core.models import Transaction
        
        transactions = Transaction.objects.filter(user_id=user_id)
        
        unpaid_fines = Decimal('0.00')
        paid_fines = Decimal('0.00')
        overdue_items = []
        
        for transaction in transactions:
            fine = self.calculator.calculate_transaction_fine(transaction)
            
            if fine > 0:
                if transaction.fine_paid:
                    paid_fines += fine
                else:
                    unpaid_fines += fine
                    
                    if not transaction.return_date:
                        overdue_items.append({
                            'item_id': transaction.library_item_id,
                            'due_date': transaction.due_date.isoformat() if transaction.due_date else None,
                            'current_fine': str(fine),
                        })
        
        can_checkout, reason = self.calculator.can_user_checkout(user_id)
        
        return {
            'user_id': user_id,
            'unpaid_fines': str(unpaid_fines),
            'paid_fines': str(paid_fines),
            'total_fines': str(unpaid_fines + paid_fines),
            'overdue_items_count': len(overdue_items),
            'overdue_items': overdue_items,
            'can_checkout': can_checkout,
            'checkout_status': reason,
        }


# Convenience functions for quick access
def calculate_fine(due_date: Union[datetime, date], 
                   return_date: Optional[Union[datetime, date]] = None) -> Decimal:
    """Quick function to calculate a fine."""
    return FineCalculator().calculate_fine(due_date, return_date)


def can_user_checkout(user_id: int) -> tuple[bool, str]:
    """Quick function to check if user can checkout."""
    return FineCalculator().can_user_checkout(user_id)
