from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.catalog.models import LibraryItem, Book, DVD, EBook


class LibraryItemTestCase(TestCase):
    """Test the base LibraryItem model."""

    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890123",
            publication_year=2020,
        )

    def test_item_creation_sets_type(self):
        """Test that item_type is automatically set by subclass."""
        self.assertEqual(self.book.item_type, LibraryItem.ItemType.BOOK)

    def test_mark_checked_out(self):
        """Test marking an available item as checked out."""
        self.assertTrue(self.book.is_available)
        self.book.mark_checked_out()
        self.assertFalse(self.book.is_available)

    def test_mark_checked_out_when_already_out(self):
        """Test that checking out an unavailable item raises error."""
        self.book.mark_checked_out()
        with self.assertRaises(ValueError):
            self.book.mark_checked_out()

    def test_mark_returned(self):
        """Test marking a checked-out item as returned."""
        self.book.mark_checked_out()
        self.book.mark_returned()
        self.assertTrue(self.book.is_available)

    def test_mark_returned_when_not_on_loan(self):
        """Test that returning an available item raises error."""
        with self.assertRaises(ValueError):
            self.book.mark_returned()

    def test_get_typed_instance(self):
        """Test that get_typed_instance returns the subclass."""
        item = LibraryItem.objects.get(pk=self.book.pk)
        typed = item.get_typed_instance()
        self.assertIsInstance(typed, Book)
        self.assertEqual(typed.author, "Test Author")

    def test_string_representation(self):
        """Test the __str__ method."""
        # Book overrides __str__ to show "title by author", not the parent format
        self.assertIn("Test Book", str(self.book))
        self.assertIn("Test Author", str(self.book))


class BookTestCase(TestCase):
    """Test the Book model."""

    def test_book_creation(self):
        """Test creating a book with required fields."""
        book = Book.objects.create(
            title="Clean Code",
            author="Robert Martin",
            isbn="9780132350884",
            publication_year=2008,
        )
        self.assertEqual(book.title, "Clean Code")
        self.assertEqual(book.author, "Robert Martin")
        self.assertEqual(book.item_type, LibraryItem.ItemType.BOOK)

    def test_default_loan_period(self):
        """Test that books have default loan period."""
        book = Book.objects.create(
            title="Test",
            author="Author",
            publication_year=2020,
        )
        self.assertEqual(book.loan_period_days, 14)

    def test_compute_due_date(self):
        """Test computing due date from loan period."""
        book = Book.objects.create(
            title="Test",
            author="Author",
            publication_year=2020,
            loan_period_days=7,
        )
        from_date = timezone.now()
        due_date = book.compute_due_date(from_date)
        expected_days = (due_date - from_date).days
        self.assertEqual(expected_days, 7)

    def test_default_condition(self):
        """Test that default condition is GOOD."""
        book = Book.objects.create(
            title="Test",
            author="Author",
            publication_year=2020,
        )
        self.assertEqual(book.condition, Book.Condition.GOOD)

    def test_book_string_representation(self):
        """Test the Book __str__ method."""
        book = Book.objects.create(
            title="1984",
            author="George Orwell",
            publication_year=1949,
        )
        self.assertEqual(str(book), "1984 by George Orwell")


class DVDTestCase(TestCase):
    """Test the DVD model."""

    def test_dvd_creation(self):
        """Test creating a DVD."""
        dvd = DVD.objects.create(
            title="Inception",
            director="Christopher Nolan",
            runtime_minutes=148,
            release_year=2010,
        )
        self.assertEqual(dvd.title, "Inception")
        self.assertEqual(dvd.director, "Christopher Nolan")
        self.assertEqual(dvd.item_type, LibraryItem.ItemType.DVD)

    def test_default_dvd_loan_period(self):
        """Test that DVDs have default loan period."""
        dvd = DVD.objects.create(
            title="Test Movie",
            director="Director",
            runtime_minutes=120,
            release_year=2020,
        )
        self.assertEqual(dvd.loan_period_days, 14)

    def test_dvd_compute_due_date(self):
        """Test computing due date for DVDs."""
        dvd = DVD.objects.create(
            title="Test",
            director="Director",
            runtime_minutes=90,
            release_year=2020,
            loan_period_days=5,
        )
        from_date = timezone.now()
        due_date = dvd.compute_due_date(from_date)
        expected_days = (due_date - from_date).days
        self.assertEqual(expected_days, 5)


class EBookTestCase(TestCase):
    """Test the EBook model."""

    def test_ebook_creation(self):
        """Test creating an eBook."""
        ebook = EBook.objects.create(
            title="Digital Book",
            author="Author Name",
            publication_year=2021,
            file_size_mb=5.2,
            file_format=EBook.Format.EPUB,
        )
        self.assertEqual(ebook.title, "Digital Book")
        self.assertEqual(ebook.item_type, LibraryItem.ItemType.EBOOK)

    def test_default_licenses(self):
        """Test that eBooks default to 1 license."""
        ebook = EBook.objects.create(
            title="Test",
            author="Author",
            publication_year=2020,
            file_size_mb=3.0,
        )
        self.assertEqual(ebook.total_licenses, 1)
        self.assertEqual(ebook.active_loans_count, 0)

    def test_ebook_mark_checked_out(self):
        """Test checking out an eBook updates loan count."""
        ebook = EBook.objects.create(
            title="Test",
            author="Author",
            publication_year=2020,
            file_size_mb=3.0,
            total_licenses=2,
        )
        ebook.mark_checked_out()
        self.assertEqual(ebook.active_loans_count, 1)
        self.assertTrue(ebook.is_available)  # Still available with 2 licenses

    def test_ebook_no_licenses_available(self):
        """Test that checking out fails when all licenses are used."""
        ebook = EBook.objects.create(
            title="Test",
            author="Author",
            publication_year=2020,
            file_size_mb=3.0,
            total_licenses=1,
        )
        ebook.mark_checked_out()
        with self.assertRaises(ValueError):
            ebook.mark_checked_out()

    def test_ebook_mark_returned(self):
        """Test returning an eBook decreases loan count."""
        ebook = EBook.objects.create(
            title="Test",
            author="Author",
            publication_year=2020,
            file_size_mb=3.0,
            total_licenses=2,
        )
        ebook.mark_checked_out()
        ebook.mark_checked_out()
        ebook.mark_returned()
        self.assertEqual(ebook.active_loans_count, 1)
        self.assertTrue(ebook.is_available)

    def test_ebook_return_without_active_loans(self):
        """Test that returning an eBook without loans raises error."""
        ebook = EBook.objects.create(
            title="Test",
            author="Author",
            publication_year=2020,
            file_size_mb=3.0,
        )
        with self.assertRaises(ValueError):
            ebook.mark_returned()

    def test_default_access_duration(self):
        """Test that eBooks have default access duration."""
        ebook = EBook.objects.create(
            title="Test",
            author="Author",
            publication_year=2020,
            file_size_mb=3.0,
        )
        self.assertEqual(ebook.access_duration_days, 21)

    def test_default_file_format(self):
        """Test that default file format is EPUB."""
        ebook = EBook.objects.create(
            title="Test",
            author="Author",
            publication_year=2020,
            file_size_mb=3.0,
        )
        self.assertEqual(ebook.file_format, EBook.Format.EPUB)

    def test_drm_protected_default(self):
        """Test that eBooks are DRM protected by default."""
        ebook = EBook.objects.create(
            title="Test",
            author="Author",
            publication_year=2020,
            file_size_mb=3.0,
        )
        self.assertTrue(ebook.drm_protected)
