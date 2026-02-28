import django_filters
from apps.catalog.models import LibraryItem, Book, DVD, EBook


class LibraryItemFilter(django_filters.FilterSet):
    """
    Unified filter for the /items/ polymorphic endpoint.
    Handles filters that work on the base LibraryItem table.
    """

    item_type = django_filters.ChoiceFilter(choices=LibraryItem.ItemType.choices)
    is_available = django_filters.BooleanFilter()
    title = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = LibraryItem
        fields = ["item_type", "is_available", "title"]


class BookFilter(django_filters.FilterSet):
    """
    Book-specific filter.
    Author and year range filters are meaningful only here.

    Polymorphic filtering challenge:
    If you query /items/?author=Martin, the LibraryItem table has no author field.
    Solution: type-specific endpoints (/books/?author=Martin) own type-specific filters.
    The unified /items/ endpoint only filters on shared fields.
    """

    author = django_filters.CharFilter(lookup_expr="icontains")
    publication_year = django_filters.NumberFilter()
    publication_year_gte = django_filters.NumberFilter(
        field_name="publication_year", lookup_expr="gte"
    )
    publication_year_lte = django_filters.NumberFilter(
        field_name="publication_year", lookup_expr="lte"
    )
    is_available = django_filters.BooleanFilter()

    class Meta:
        model = Book
        fields = ["author", "publication_year", "is_available"]


class DVDFilter(django_filters.FilterSet):
    director = django_filters.CharFilter(lookup_expr="icontains")
    release_year = django_filters.NumberFilter()
    is_available = django_filters.BooleanFilter()

    class Meta:
        model = DVD
        fields = ["director", "release_year", "is_available"]


class EBookFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(lookup_expr="icontains")
    file_format = django_filters.ChoiceFilter(choices=[
        ("PDF", "PDF"), ("EPUB", "EPUB"), ("MOBI", "MOBI"),
    ])
    is_available = django_filters.BooleanFilter()
    drm_protected = django_filters.BooleanFilter()

    class Meta:
        model = EBook
        fields = ["author", "file_format", "is_available", "drm_protected"]
