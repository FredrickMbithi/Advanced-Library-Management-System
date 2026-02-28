from decimal import Decimal
from datetime import timedelta
from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from apps.catalog.models import Book, DVD, EBook
from apps.loans.models import Loan
from apps.loans.services import LoanService, FineCalculator

User = get_user_model()


# ─── Fixtures ────────────────────────────────────────────────────────────────

class BaseTestCase(TestCase):
    """Shared setup for domain-layer tests."""

    def setUp(self):
        self.member = User.objects.create_user(
            username="alice", password="pass", role=User.Role.MEMBER
        )
        self.librarian = User.objects.create_user(
            username="librarian", password="pass", role=User.Role.LIBRARIAN
        )
        self.book = Book.objects.create(
            title="Clean Code",
            author="Robert Martin",
            publication_year=2008,
            loan_period_days=14,
        )
        self.ebook = EBook.objects.create(
            title="The Pragmatic Programmer",
            author="Hunt & Thomas",
            publication_year=1999,
            file_size_mb=Decimal("5.2"),
            total_licenses=2,
        )


# ─── FineCalculator Tests ────────────────────────────────────────────────────

class FineCalculatorTests(BaseTestCase):

    def _make_overdue_loan(self, days_overdue=5):
        """Helper: create a loan that is overdue by N days."""
        loan = Loan.objects.create(
            item=self.book,
            borrower=self.member,
            borrowed_at=timezone.now() - timedelta(days=days_overdue + 14),
            due_at=timezone.now() - timedelta(days=days_overdue),
        )
        self.book.is_available = False
        self.book.save()
        return loan

    def test_no_fine_when_not_overdue(self):
        loan = Loan.objects.create(
            item=self.book,
            borrower=self.member,
            due_at=timezone.now() + timedelta(days=7),
        )
        self.assertEqual(FineCalculator.compute(loan), Decimal("0.00"))

    def test_fine_is_one_dollar_per_day(self):
        loan = self._make_overdue_loan(days_overdue=5)
        self.assertEqual(FineCalculator.compute(loan), Decimal("5.00"))

    def test_returned_loan_accrues_no_fine(self):
        loan = self._make_overdue_loan(days_overdue=5)
        loan.returned_at = timezone.now()
        loan.save()
        # is_overdue is False once returned
        self.assertFalse(loan.is_overdue)
        self.assertEqual(FineCalculator.compute(loan), Decimal("0.00"))

    def test_user_blocked_at_threshold(self):
        self._make_overdue_loan(days_overdue=10)  # $10 fine
        self.assertTrue(FineCalculator.user_is_blocked(self.member))

    def test_user_not_blocked_below_threshold(self):
        self._make_overdue_loan(days_overdue=9)  # $9 fine
        self.assertFalse(FineCalculator.user_is_blocked(self.member))

    def test_total_fines_sum_across_multiple_loans(self):
        book2 = Book.objects.create(
            title="Refactoring", author="Fowler", publication_year=2018,
        )
        Loan.objects.create(
            item=self.book, borrower=self.member,
            due_at=timezone.now() - timedelta(days=3),
        )
        self.book.is_available = False
        self.book.save()
        Loan.objects.create(
            item=book2, borrower=self.member,
            due_at=timezone.now() - timedelta(days=4),
        )
        book2.is_available = False
        book2.save()
        total = FineCalculator.compute_total_for_user(self.member)
        self.assertEqual(total, Decimal("7.00"))


# ─── LoanService Checkout Tests ──────────────────────────────────────────────

class LoanCheckoutTests(BaseTestCase):

    def test_successful_checkout_creates_loan(self):
        loan = LoanService.checkout(self.book, self.member)
        self.assertIsNotNone(loan.pk)
        self.assertEqual(loan.borrower, self.member)
        self.book.refresh_from_db()
        self.assertFalse(self.book.is_available)

    def test_checkout_unavailable_item_raises(self):
        self.book.is_available = False
        self.book.save()
        with self.assertRaises(ValueError):
            LoanService.checkout(self.book, self.member)

    def test_double_checkout_same_user_raises(self):
        LoanService.checkout(self.book, self.member)
        with self.assertRaises(ValueError):
            LoanService.checkout(self.book, self.member)

    def test_blocked_user_cannot_checkout(self):
        # Create $10 fine
        Loan.objects.create(
            item=self.book,
            borrower=self.member,
            due_at=timezone.now() - timedelta(days=10),
        )
        self.book.is_available = False
        self.book.save()

        book2 = Book.objects.create(
            title="SICP", author="Abelson", publication_year=1984,
        )
        with self.assertRaises(PermissionError):
            LoanService.checkout(book2, self.member)

    def test_due_date_set_from_loan_period(self):
        self.book.loan_period_days = 21
        self.book.save()
        loan = LoanService.checkout(self.book, self.member)
        expected_due = timezone.now() + timedelta(days=21)
        # Allow 5 second tolerance for test execution time
        self.assertAlmostEqual(
            loan.due_at.timestamp(),
            expected_due.timestamp(),
            delta=5,
        )

    def test_ebook_checkout_decrements_licenses(self):
        loan = LoanService.checkout(self.ebook, self.member)
        self.ebook.refresh_from_db()
        self.assertEqual(self.ebook.active_loans_count, 1)
        self.assertTrue(self.ebook.is_available)  # 1 license still free

    def test_ebook_fully_loaned_out_is_unavailable(self):
        member2 = User.objects.create_user(username="bob", password="pass")
        LoanService.checkout(self.ebook, self.member)
        LoanService.checkout(self.ebook, member2)
        self.ebook.refresh_from_db()
        self.assertFalse(self.ebook.is_available)


# ─── LoanService Return Tests ────────────────────────────────────────────────

class LoanReturnTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.loan = LoanService.checkout(self.book, self.member)

    def test_successful_return_marks_returned_at(self):
        returned_loan = LoanService.return_item(self.loan, self.member)
        self.assertIsNotNone(returned_loan.returned_at)
        self.book.refresh_from_db()
        self.assertTrue(self.book.is_available)

    def test_cannot_return_already_returned_item(self):
        LoanService.return_item(self.loan, self.member)
        self.loan.refresh_from_db()
        with self.assertRaises(ValueError):
            LoanService.return_item(self.loan, self.member)

    def test_wrong_user_cannot_return(self):
        other_member = User.objects.create_user(username="charlie", password="pass")
        with self.assertRaises(PermissionError):
            LoanService.return_item(self.loan, other_member)

    def test_librarian_cannot_return_on_behalf_of_member(self):
        """Librarians manage catalog, not return items for members."""
        with self.assertRaises(PermissionError):
            LoanService.return_item(self.loan, self.librarian)


# ─── Loan Derived State Tests ────────────────────────────────────────────────

class LoanStateTests(BaseTestCase):

    def test_active_loan_is_active(self):
        loan = Loan(
            item=self.book,
            borrower=self.member,
            due_at=timezone.now() + timedelta(days=7),
        )
        self.assertTrue(loan.is_active)
        self.assertFalse(loan.is_overdue)

    def test_overdue_loan_detected_correctly(self):
        loan = Loan(
            item=self.book,
            borrower=self.member,
            borrowed_at=timezone.now() - timedelta(days=20),
            due_at=timezone.now() - timedelta(days=5),
        )
        self.assertTrue(loan.is_overdue)
        self.assertEqual(loan.days_overdue, 5)

    def test_returned_loan_is_not_overdue(self):
        loan = Loan(
            item=self.book,
            borrower=self.member,
            due_at=timezone.now() - timedelta(days=5),
            returned_at=timezone.now(),
        )
        self.assertFalse(loan.is_overdue)


# ─── API Permission Tests ─────────────────────────────────────────────────────

class PermissionAPITests(APITestCase):

    def setUp(self):
        self.member = User.objects.create_user(
            username="alice", password="pass", role=User.Role.MEMBER
        )
        self.librarian = User.objects.create_user(
            username="lib", password="pass", role=User.Role.LIBRARIAN
        )
        self.book = Book.objects.create(
            title="Test Book", author="Author", publication_year=2020,
        )

    def test_anonymous_can_read_catalog(self):
        response = self.client.get("/books/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_member_cannot_create_book(self):
        self.client.force_authenticate(self.member)
        response = self.client.post("/books/", {
            "title": "New Book", "author": "Author",
            "publication_year": 2021, "loan_period_days": 14,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_librarian_can_create_book(self):
        self.client.force_authenticate(self.librarian)
        response = self.client.post("/books/", {
            "title": "New Book", "author": "Author",
            "publication_year": 2021, "loan_period_days": 14,
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_member_cannot_view_other_members_loans(self):
        other = User.objects.create_user(username="other", password="pass")
        loan = Loan.objects.create(
            item=self.book, borrower=other,
            due_at=timezone.now() + timedelta(days=7),
        )
        self.client.force_authenticate(self.member)
        response = self.client.get(f"/loans/{loan.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_librarian_can_view_any_loan(self):
        loan = Loan.objects.create(
            item=self.book, borrower=self.member,
            due_at=timezone.now() + timedelta(days=7),
        )
        self.client.force_authenticate(self.librarian)
        response = self.client.get(f"/loans/{loan.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
