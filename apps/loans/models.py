from django.db import models
from django.utils import timezone
from django.conf import settings
from decimal import Decimal


class Loan(models.Model):
    """
    Loan lifecycle model.

    Design decisions:
    - item FK → LibraryItem (concrete base). Works for all item types.
    - returned_at=None means active loan. No status field. No drift.
    - fine_amount is NOT stored — computed by FineCalculator service.
    - due_at is set at creation from item's loan_period. Never changes.

    State machine (derived, never stored):
        borrowed_at set, returned_at=None, due_at > now  → ACTIVE
        borrowed_at set, returned_at=None, due_at < now  → OVERDUE
        returned_at set                                  → RETURNED
    """

    item = models.ForeignKey(
        "catalog.LibraryItem",
        on_delete=models.PROTECT,  # Never delete items with loan history
        related_name="loans",
    )
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="loans",
    )
    borrowed_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField()  # Set by LoanService, not user
    returned_at = models.DateTimeField(null=True, blank=True, db_index=True)

    # --- Derived state properties (no DB column) ---

    @property
    def is_active(self) -> bool:
        return self.returned_at is None

    @property
    def is_returned(self) -> bool:
        return self.returned_at is not None

    @property
    def is_overdue(self) -> bool:
        return self.is_active and timezone.now() > self.due_at

    @property
    def days_overdue(self) -> int:
        if not self.is_overdue:
            return 0
        delta = timezone.now() - self.due_at
        return max(0, delta.days)

    # --- Fine hint (actual calculation delegated to FineCalculator) ---

    @property
    def fine_preview(self) -> Decimal:
        """
        Convenience property for serializer display only.
        Do NOT use this for business logic — use FineCalculator service.
        """
        from apps.loans.services import FineCalculator
        return FineCalculator.compute(self)

    def __str__(self):
        status = "active" if self.is_active else "returned"
        return f"Loan: {self.borrower} → {self.item} [{status}]"

    class Meta:
        db_table = "loans_loan"
        ordering = ["-borrowed_at"]
        constraints = [
            # Prevent double checkout at DB level — not just app level
            models.UniqueConstraint(
                fields=["item", "borrower"],
                condition=models.Q(returned_at__isnull=True),
                name="unique_active_loan_per_item_borrower",
            )
        ]
