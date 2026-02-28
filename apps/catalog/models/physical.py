from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .base import LibraryItem


class PhysicalItemMixin(models.Model):
    """
    Abstract mixin — adds physical-world fields.
    No DB table. No extra JOIN.
    Shared by Book and DVD only.
    """

    class Condition(models.TextChoices):
        NEW = "NEW", "New"
        GOOD = "GOOD", "Good"
        FAIR = "FAIR", "Fair"
        POOR = "POOR", "Poor"

    condition = models.CharField(
        max_length=10,
        choices=Condition.choices,
        default=Condition.GOOD,
    )
    loan_period_days = models.PositiveIntegerField(
        default=14,
        validators=[MinValueValidator(1), MaxValueValidator(90)],
    )

    def compute_due_date(self, from_date=None):
        """
        Due date is computed from loan period.
        Centralised here so both Book and DVD inherit it.
        """
        from datetime import timedelta
        base = from_date or timezone.now()
        return base + timedelta(days=self.loan_period_days)

    class Meta:
        abstract = True


class Book(PhysicalItemMixin, LibraryItem):
    """
    Extends LibraryItem (multi-table) + PhysicalItemMixin (abstract).
    Only Book-specific fields here.
    """

    author = models.CharField(max_length=255, db_index=True)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    publication_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1450),  # Gutenberg press era
            MaxValueValidator(timezone.now().year),
        ]
    )
    publisher = models.CharField(max_length=255, blank=True)
    page_count = models.PositiveIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.item_type = LibraryItem.ItemType.BOOK
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        db_table = "catalog_book"


class DVD(PhysicalItemMixin, LibraryItem):
    """Physical DVD. loan_period shorter by default."""

    director = models.CharField(max_length=255, db_index=True)
    runtime_minutes = models.PositiveIntegerField()
    release_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1888),  # First film ever
            MaxValueValidator(timezone.now().year),
        ]
    )
    studio = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        self.item_type = LibraryItem.ItemType.DVD
        self.loan_period_days = self.loan_period_days or 7  # DVDs: 7 days default
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.release_year}) — dir. {self.director}"

    class Meta:
        db_table = "catalog_dvd"
