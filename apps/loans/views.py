from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.catalog.models import LibraryItem
from apps.loans.models import Loan
from apps.loans.serializers import LoanSerializer, LoanCreateSerializer, ReturnSerializer
from apps.loans.services import LoanService, FineCalculator
from apps.accounts.permissions import (
    IsOwnerOrLibrarian, IsMemberWithBorrowingPrivilege,
)


# ─── Loan Views ─────────────────────────────────────────────────────────────────

class LoanListView(generics.ListAPIView):
    """
    GET /loans/
    Members see only their loans.
    Librarians see all loans.
    """
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Loan.objects.select_related("item", "borrower")
        if user.is_librarian:
            return qs.all()
        return qs.filter(borrower=user)


class LoanCreateView(APIView):
    """
    POST /loans/
    Checkout flow fully delegated to LoanService.
    View owns: auth check, input parsing, HTTP response shape.
    View does NOT own: business rules.
    """
    permission_classes = [IsAuthenticated, IsMemberWithBorrowingPrivilege]

    def post(self, request):
        serializer = LoanCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_id = serializer.validated_data["item_id"]

        try:
            item = LibraryItem.objects.get(pk=item_id)
            loan = LoanService.checkout(item=item, borrower=request.user)
        except (ValueError, PermissionError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)


class LoanDetailView(generics.RetrieveAPIView):
    """GET /loans/:id/"""
    queryset = Loan.objects.select_related("item", "borrower")
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrLibrarian]


class LoanReturnView(APIView):
    """
    POST /loans/:id/return/
    Resource-oriented return. Not /items/:id/return/ — the action
    belongs to the Loan resource, not the Item resource.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            loan = Loan.objects.select_related("item", "borrower").get(pk=pk)
        except Loan.DoesNotExist:
            return Response({"detail": "Loan not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReturnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            loan = LoanService.return_item(loan=loan, returning_user=request.user)
        except (ValueError, PermissionError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(LoanSerializer(loan).data, status=status.HTTP_200_OK)


class UserFineView(APIView):
    """
    GET /users/me/fines/
    Returns outstanding fine total for authenticated user.
    Fine computation fully delegated to FineCalculator.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total = FineCalculator.compute_total_for_user(request.user)
        blocked = FineCalculator.user_is_blocked(request.user)
        return Response({
            "outstanding_fines": str(total),
            "borrowing_blocked": blocked,
            "block_threshold": str(FineCalculator.rate_per_day * 10),  # informational
        })
