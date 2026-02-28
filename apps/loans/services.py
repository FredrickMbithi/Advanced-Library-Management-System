from decimal import Decimal
from django.utils import timezone
from django.db import transaction


FINE_RATE_PER_DAY = Decimal("1.00")
FINE_BLOCK_THRESHOLD = Decimal("10.00")


class FineCalculator:
    """
    Pure domain service. No Django model imports at class level.
    Stateless. Fully unit-testable without DB.

    Why a class, not module-level functions?
    - Allows subclassing for different fine policies (e.g., student rate).
    - Rate can be injected for testing without monkey-patching globals.
    """

    rate_per_day: Decimal = FINE_RATE_PER_DAY

    @classmethod
    def compute(cls, loan) -> Decimal:
        """Compute fine for a single loan."""
        if not loan.is_overdue:
            return Decimal("0.00")
        return Decimal(loan.days_overdue) * cls.rate_per_day

    @classmethod
    def compute_total_for_user(cls, user) -> Decimal:
        """
        Sum outstanding fines across all active overdue loans.
        Only active loans — returned loans' fines are historical.
        """
        from apps.loans.models import Loan  # Late import avoids circular deps
        active_loans = Loan.objects.filter(
            borrower=user,
            returned_at__isnull=True,
        ).select_related("item")

        return sum(
            (cls.compute(loan) for loan in active_loans),
            Decimal("0.00"),
        )

    @classmethod
    def user_is_blocked(cls, user) -> bool:
        total = cls.compute_total_for_user(user)
        return total >= FINE_BLOCK_THRESHOLD


class LoanService:
    """
    Orchestrates the full loan lifecycle.
    Owns: validation, state transitions, fine checks.
    Views call this. Views own NOTHING domain-related.
    """

    @staticmethod
    @transaction.atomic
    def checkout(item, borrower) -> "Loan":
        """
        Full checkout flow:
        1. Check borrower eligibility (fines)
        2. Check item availability
        3. Prevent double checkout (app-level guard + DB constraint)
        4. Set due_at from item's loan period
        5. Create Loan, mark item unavailable
        """
        from apps.loans.models import Loan
        from apps.catalog.models import LibraryItem

        # 1. Fine block check
        if FineCalculator.user_is_blocked(borrower):
            outstanding = FineCalculator.compute_total_for_user(borrower)
            raise PermissionError(
                f"Borrowing blocked. Outstanding fines: ${outstanding:.2f}. "
                f"Threshold: ${FINE_BLOCK_THRESHOLD:.2f}."
            )

        # 2. Availability check
        typed_item = item.get_typed_instance()
        if not typed_item.is_available:
            raise ValueError(f"'{item.title}' is not available for checkout.")

        # 3. Double checkout guard (belt-and-suspenders with DB constraint)
        if Loan.objects.filter(item=item, borrower=borrower, returned_at__isnull=True).exists():
            raise ValueError(f"You already have '{item.title}' checked out.")

        # 4. Compute due date from item type
        due_at = LoanService._compute_due_date(typed_item)

        # 5. Create loan + mark item
        loan = Loan.objects.create(
            item=item,
            borrower=borrower,
            due_at=due_at,
        )
        typed_item.mark_checked_out()

        return loan

    @staticmethod
    @transaction.atomic
    def return_item(loan, returning_user) -> "Loan":
        """
        Full return flow:
        1. Validate loan is active
        2. Validate correct user is returning
        3. Mark returned_at
        4. Mark item available
        """
        if loan.is_returned:
            raise ValueError("This item has already been returned.")

        if loan.borrower_id != returning_user.pk:
            raise PermissionError("You cannot return an item borrowed by another user.")

        loan.returned_at = timezone.now()
        loan.save(update_fields=["returned_at"])

        typed_item = loan.item.get_typed_instance()
        typed_item.mark_returned()

        return loan

    @staticmethod
    def _compute_due_date(typed_item):
        """
        Delegate due date to the item itself.
        Physical items have loan_period_days.
        Digital items use access_duration_days.
        """
        from apps.catalog.models import EBook
        if isinstance(typed_item, EBook):
            from datetime import timedelta
            return timezone.now() + timedelta(days=typed_item.access_duration_days)
        # PhysicalItemMixin provides compute_due_date()
        if hasattr(typed_item, "compute_due_date"):
            return typed_item.compute_due_date()
        raise NotImplementedError(
            f"Item type {type(typed_item)} does not implement due date logic."
        )
