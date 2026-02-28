from rest_framework import serializers
from django.utils import timezone
from apps.catalog.models import LibraryItem, Book, DVD, EBook


class LibraryItemSerializer(serializers.ModelSerializer):
    """Base serializer — used for list views and as nested representation."""

    item_type_display = serializers.CharField(source="get_item_type_display", read_only=True)

    class Meta:
        model = LibraryItem
        fields = ["id", "title", "item_type", "item_type_display", "is_available", "created_at"]
        read_only_fields = ["item_type", "is_available", "created_at"]


class BookSerializer(serializers.ModelSerializer):
    """
    Full Book serializer.
    Validation lives here only when it's input validation.
    Business rules (e.g., can this book be loaned?) live in services.
    """

    class Meta:
        model = Book
        fields = [
            "id", "title", "author", "isbn", "publication_year",
            "publisher", "page_count", "condition", "loan_period_days",
            "is_available", "created_at",
        ]
        read_only_fields = ["is_available", "created_at"]

    def validate_publication_year(self, value):
        current_year = timezone.now().year
        if value < 1450:
            raise serializers.ValidationError(
                "Publication year cannot predate the printing press (1450)."
            )
        if value > current_year:
            raise serializers.ValidationError(
                f"Publication year cannot be in the future (max: {current_year})."
            )
        return value

    def validate_isbn(self, value):
        if value and not (len(value) in (10, 13)) :
            raise serializers.ValidationError("ISBN must be 10 or 13 characters.")
        return value


class DVDSerializer(serializers.ModelSerializer):

    class Meta:
        model = DVD
        fields = [
            "id", "title", "director", "runtime_minutes", "release_year",
            "studio", "condition", "loan_period_days", "is_available", "created_at",
        ]
        read_only_fields = ["is_available", "created_at"]

    def validate_release_year(self, value):
        current_year = timezone.now().year
        if value < 1888:
            raise serializers.ValidationError(
                "Release year cannot predate cinema (1888)."
            )
        if value > current_year:
            raise serializers.ValidationError("Release year cannot be in the future.")
        return value


class EBookSerializer(serializers.ModelSerializer):

    class Meta:
        model = EBook
        fields = [
            "id", "title", "author", "isbn", "publication_year",
            "file_format", "file_size_mb", "drm_protected",
            "total_licenses", "active_loans_count",
            "access_duration_days", "is_available", "created_at",
        ]
        read_only_fields = ["is_available", "active_loans_count", "created_at"]


# --- Polymorphic serializer for unified item endpoints ---

ITEM_SERIALIZER_MAP = {
    LibraryItem.ItemType.BOOK: BookSerializer,
    LibraryItem.ItemType.DVD: DVDSerializer,
    LibraryItem.ItemType.EBOOK: EBookSerializer,
}


class PolymorphicLibraryItemSerializer(serializers.BaseSerializer):
    """
    Routes to the correct serializer based on item_type.
    Used in read-only list/detail views for /items/ endpoint.
    Write operations hit type-specific endpoints (/books/, /dvds/, etc.)
    """

    def to_representation(self, instance):
        serializer_class = ITEM_SERIALIZER_MAP.get(instance.item_type)
        if serializer_class is None:
            return LibraryItemSerializer(instance).data
        typed_instance = instance.get_typed_instance()
        return serializer_class(typed_instance, context=self.context).data
