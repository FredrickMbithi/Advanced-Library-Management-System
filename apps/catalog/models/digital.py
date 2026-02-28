from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .base import LibraryItem


class DigitalItemMixin(models.Model):
    """
    Abstract mixin for digital items.
    No loan period — digital items don't have physical return constraints.
    Access expiry handled differently (see EBook).
    """

    class Format(models.TextChoices):
        PDF = "PDF", "PDF"
        EPUB = "EPUB", "EPUB"
        MOBI = "MOBI", "MOBI"
        MP4 = "MP4", "MP4"

    file_size_mb = models.DecimalField(max_digits=8, decimal_places=2)
    drm_protected = models.BooleanField(default=True)
    download_url = models.URLField(blank=True)  # Signed URL in production

    class Meta:
        abstract = True


class EBook(DigitalItemMixin, LibraryItem):
    """
    Digital item. Key design difference:
    - No loan_period_days (digital access uses access_duration_days)
    - Can allow simultaneous access (is_available always True if copies > 0)
    - DRM governs real access control
    """

    author = models.CharField(max_length=255, db_index=True)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    publication_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1450),
            MaxValueValidator(timezone.now().year),
        ]
    )
    file_format = models.CharField(
        max_length=10,
        choices=DigitalItemMixin.Format.choices,
        default=DigitalItemMixin.Format.EPUB,
    )
    # EBooks may allow N simultaneous checkouts (copies = licenses purchased)
    total_licenses = models.PositiveIntegerField(default=1)
    active_loans_count = models.PositiveIntegerField(default=0)

    access_duration_days = models.PositiveIntegerField(
        default=21,
        help_text="How long a borrower can access the eBook after checkout.",
    )

    # --- Override availability logic for digital items ---

    def mark_checked_out(self):
        """
        EBooks: availability is license-count based, not binary.
        Overrides base class to handle concurrent access.
        """
        if self.active_loans_count >= self.total_licenses:
            raise ValueError(f"No licenses available for '{self.title}'.")
        self.active_loans_count += 1
        self.is_available = self.active_loans_count < self.total_licenses
        self.save(update_fields=["active_loans_count", "is_available", "updated_at"])

    def mark_returned(self):
        if self.active_loans_count <= 0:
            raise ValueError(f"No active loans to return for '{self.title}'.")
        self.active_loans_count -= 1
        self.is_available = True
        self.save(update_fields=["active_loans_count", "is_available", "updated_at"])

    def save(self, *args, **kwargs):
        self.item_type = LibraryItem.ItemType.EBOOK
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.author} [{self.file_format}]"

    class Meta:
        db_table = "catalog_ebook"
