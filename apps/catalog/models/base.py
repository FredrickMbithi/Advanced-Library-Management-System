from django.db import models
from django.utils import timezone


class LibraryItem(models.Model):
    """
    Concrete base table. ALL loanable items FK here.
    Shared fields only — no type-specific leakage.

    Why concrete (not abstract):
    - Loan.item = FK(LibraryItem) requires a real table.
    - Enables LibraryItem.objects.all() across item types.
    - Polymorphic access via item.book / item.dvd / item.ebook
    """

    class ItemType(models.TextChoices):
        BOOK = "BOOK", "Book"
        DVD = "DVD", "DVD"
        EBOOK = "EBOOK", "E-Book"

    title = models.CharField(max_length=255, db_index=True)
    item_type = models.CharField(
        max_length=10,
        choices=ItemType.choices,
        editable=False,  # Set by subclass, not user input
    )
    is_available = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --- Domain methods ---

    def mark_checked_out(self):
        """State transition. Business rule lives here, not in views."""
        if not self.is_available:
            raise ValueError(f"Item '{self.title}' is already checked out.")
        self.is_available = False
        self.save(update_fields=["is_available", "updated_at"])

    def mark_returned(self):
        if self.is_available:
            raise ValueError(f"Item '{self.title}' is not currently on loan.")
        self.is_available = True
        self.save(update_fields=["is_available", "updated_at"])

    def get_typed_instance(self):
        """
        Returns the subclass instance (Book, DVD, EBook).
        Avoids try/except chains in views.
        """
        for attr in ("book", "dvd", "ebook"):
            if hasattr(self, attr):
                return getattr(self, attr)
        return self

    def __str__(self):
        return f"[{self.item_type}] {self.title}"

    class Meta:
        db_table = "catalog_library_item"
        ordering = ["title"]
