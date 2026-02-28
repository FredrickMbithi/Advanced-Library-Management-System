from rest_framework.permissions import BasePermission, IsAuthenticatedOrReadOnly, SAFE_METHODS


class IsLibrarianOrReadOnly(BasePermission):
    """
    - Anonymous/Members: GET, HEAD, OPTIONS only.
    - Librarians: full access.

    Use on catalog endpoints where only librarians add/edit items.
    """

    message = "Only librarians can modify catalog items."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_librarian
        )


class IsLibrarian(BasePermission):
    """Hard gate — only librarians. No read access for others."""

    message = "This action is restricted to librarians."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_librarian
        )


class IsOwnerOrLibrarian(BasePermission):
    """
    Object-level permission.
    A loan is visible/modifiable only by its borrower or a librarian.
    """

    message = "You do not have permission to access this loan."

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_librarian:
            return True
        # obj is a Loan instance
        return obj.borrower_id == request.user.pk


class IsMemberWithBorrowingPrivilege(BasePermission):
    """
    Checked at checkout time.
    Delegates fine check to the service layer (no logic here).
    """

    message = "Your borrowing privilege is suspended due to outstanding fines."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        from apps.loans.services import FineCalculator
        return not FineCalculator.user_is_blocked(request.user)
