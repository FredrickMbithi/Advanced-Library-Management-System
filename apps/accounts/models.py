from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal


class User(AbstractUser):
    """
    Domain-driven User model.
    Role is a first-class concept, not a permission hack.
    """

    class Role(models.TextChoices):
        MEMBER = "MEMBER", "Member"
        LIBRARIAN = "LIBRARIAN", "Librarian"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )

    FINE_BLOCK_THRESHOLD = Decimal("10.00")  # Configurable per environment

    # --- Domain properties (pure Python, no DB hit) ---

    @property
    def is_librarian(self) -> bool:
        return self.role == self.Role.LIBRARIAN

    @property
    def is_member(self) -> bool:
        return self.role == self.Role.MEMBER

    def can_borrow(self, outstanding_fines: Decimal) -> bool:
        """
        Encapsulates borrowing eligibility.
        Fine threshold check is injected — caller (service) computes fines.
        This keeps the model free of cross-app imports.
        """
        return outstanding_fines < self.FINE_BLOCK_THRESHOLD

    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        db_table = "accounts_user"
        verbose_name = "User"
