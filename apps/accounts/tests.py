from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTestCase(TestCase):
    """Test the custom User model."""

    def setUp(self):
        self.member = User.objects.create_user(
            username="member1",
            password="testpass123",
            role=User.Role.MEMBER
        )
        self.librarian = User.objects.create_user(
            username="librarian1",
            password="testpass123",
            role=User.Role.LIBRARIAN
        )

    def test_user_creation(self):
        """Test that users are created with correct roles."""
        self.assertEqual(self.member.role, User.Role.MEMBER)
        self.assertEqual(self.librarian.role, User.Role.LIBRARIAN)

    def test_is_librarian_property(self):
        """Test the is_librarian property."""
        self.assertTrue(self.librarian.is_librarian)
        self.assertFalse(self.member.is_librarian)

    def test_is_member_property(self):
        """Test the is_member property."""
        self.assertTrue(self.member.is_member)
        self.assertFalse(self.librarian.is_member)

    def test_can_borrow_with_low_fines(self):
        """Test that users can borrow when fines are below threshold."""
        outstanding_fines = Decimal("5.00")
        self.assertTrue(self.member.can_borrow(outstanding_fines))

    def test_cannot_borrow_with_high_fines(self):
        """Test that users cannot borrow when fines exceed threshold."""
        outstanding_fines = Decimal("15.00")
        self.assertFalse(self.member.can_borrow(outstanding_fines))

    def test_can_borrow_at_threshold(self):
        """Test borrowing eligibility at the exact threshold."""
        outstanding_fines = User.FINE_BLOCK_THRESHOLD
        self.assertFalse(self.member.can_borrow(outstanding_fines))

    def test_user_string_representation(self):
        """Test the __str__ method."""
        self.assertEqual(str(self.member), "member1 (MEMBER)")
        self.assertEqual(str(self.librarian), "librarian1 (LIBRARIAN)")

    def test_default_role_is_member(self):
        """Test that the default role is MEMBER."""
        user = User.objects.create_user(username="testuser", password="pass")
        self.assertEqual(user.role, User.Role.MEMBER)
