"""
core/views.py - The Gatekeeper (API Endpoints)

This module contains the API views that handle HTTP requests.
Views act as the gatekeeper, performing validation and delegating
business logic to the appropriate service classes.

Endpoints:
- LibraryItems: CRUD for library items
- Checkout: Process item checkouts
- Return: Process item returns
- Fines: View and pay fines
- UserProfile: User management
"""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

from .models import LibraryItem, Transaction, UserProfile
from .serializers import (
    LibraryItemSerializer,
    LibraryItemListSerializer,
    TransactionSerializer,
    UserProfileSerializer,
    CheckoutRequestSerializer,
    ReturnRequestSerializer,
    FinePaymentSerializer,
)
from .logic.calculator import FineCalculator, FineReport


class LibraryItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for LibraryItem CRUD operations.
    
    Provides:
    - GET /api/items/ - List all items
    - POST /api/items/ - Create new item
    - GET /api/items/{id}/ - Get item details
    - PUT /api/items/{id}/ - Update item
    - DELETE /api/items/{id}/ - Delete item
    - GET /api/items/available/ - List available items
    - GET /api/items/search/?q=query - Search items
    """
    
    queryset = LibraryItem.objects.all()
    serializer_class = LibraryItemSerializer
    
    def get_serializer_class(self):
        """Use lightweight serializer for list views."""
        if self.action == 'list':
            return LibraryItemListSerializer
        return LibraryItemSerializer
    
    def get_queryset(self):
        """Allow filtering by various parameters."""
        queryset = LibraryItem.objects.all()
        
        # Filter by item type
        item_type = self.request.query_params.get('type')
        if item_type:
            queryset = queryset.filter(item_type=item_type)
        
        # Filter by availability
        available = self.request.query_params.get('available')
        if available is not None:
            queryset = queryset.filter(is_available=available.lower() == 'true')
        
        # Filter by genre
        genre = self.request.query_params.get('genre')
        if genre:
            queryset = queryset.filter(genre__icontains=genre)
        
        # Filter by digital/physical
        digital = self.request.query_params.get('digital')
        if digital is not None:
            queryset = queryset.filter(is_digital=digital.lower() == 'true')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available items."""
        items = LibraryItem.objects.filter(is_available=True)
        serializer = LibraryItemListSerializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search items by title, author, or genre.
        
        Query params:
        - q: Search query string
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {'error': 'Search query parameter "q" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        items = LibraryItem.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(genre__icontains=query) |
            Q(isbn__icontains=query)
        )
        
        serializer = LibraryItemListSerializer(items, many=True)
        return Response({
            'count': items.count(),
            'query': query,
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get all transactions for a specific item."""
        item = self.get_object()
        transactions = item.transactions.all()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class CheckoutView(APIView):
    """
    API endpoint for checking out library items.
    
    POST /api/checkout/
    
    Request body:
    {
        "user_id": int,
        "item_id": int,
        "custom_due_date": datetime (optional)
    }
    
    Validation rules:
    1. User must exist and have fines <= $50
    2. User must not exceed checkout limit
    3. Physical items must be available
    """
    
    def post(self, request):
        """Process a checkout request."""
        serializer = CheckoutRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_id = serializer.validated_data['user_id']
        item_id = serializer.validated_data['item_id']
        custom_due_date = serializer.validated_data.get('custom_due_date')
        
        # Get the user and item
        user = User.objects.get(id=user_id)
        item = LibraryItem.objects.get(id=item_id)
        
        # Calculate due date
        if custom_due_date:
            due_date = custom_due_date
        else:
            due_date = timezone.now() + timedelta(days=item.get_loan_period_days())
        
        # Create the transaction
        transaction = Transaction.objects.create(
            user=user,
            library_item=item,
            due_date=due_date,
            status='checked_out'
        )
        
        # Update item availability (for physical items)
        if not item.is_digital:
            item.is_available = False
            item.save()
        
        return Response({
            'success': True,
            'message': f"Successfully checked out '{item.title}'",
            'transaction': TransactionSerializer(transaction).data
        }, status=status.HTTP_201_CREATED)


class ReturnView(APIView):
    """
    API endpoint for returning library items.
    
    POST /api/return/
    
    Request body:
    {
        "transaction_id": int,
        OR
        "user_id": int,
        "item_id": int,
        
        "return_date": datetime (optional, defaults to now)
    }
    """
    
    def post(self, request):
        """Process a return request."""
        serializer = ReturnRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction = serializer.validated_data['transaction']
        return_date = serializer.validated_data.get('return_date') or timezone.now()
        
        # Get the item before updating transaction
        item = transaction.library_item
        
        # Calculate fine before marking as returned
        calculator = FineCalculator()
        fine_amount = calculator.calculate_fine(transaction.due_date, return_date)
        
        # Update transaction
        transaction.return_date = return_date
        transaction.status = 'returned'
        transaction.fine_amount = fine_amount
        transaction.save()
        
        # Update item availability (for physical items)
        if not item.is_digital:
            item.is_available = True
            item.save()
        
        response_data = {
            'success': True,
            'message': f"Successfully returned '{item.title}'",
            'transaction': TransactionSerializer(transaction).data,
        }
        
        if fine_amount > 0:
            response_data['fine'] = {
                'amount': str(fine_amount),
                'message': f"A fine of ${fine_amount} has been applied for late return"
            }
        
        return Response(response_data)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing transactions.
    
    Provides:
    - GET /api/transactions/ - List all transactions
    - GET /api/transactions/{id}/ - Get transaction details
    - GET /api/transactions/active/ - List active checkouts
    - GET /api/transactions/overdue/ - List overdue items
    """
    
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        """Allow filtering by user and status."""
        queryset = Transaction.objects.all()
        
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        item_id = self.request.query_params.get('item_id')
        if item_id:
            queryset = queryset.filter(library_item_id=item_id)
        
        transaction_status = self.request.query_params.get('status')
        if transaction_status:
            queryset = queryset.filter(status=transaction_status)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active (non-returned) transactions."""
        transactions = Transaction.objects.filter(
            status__in=['checked_out', 'overdue']
        )
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue transactions."""
        now = timezone.now()
        transactions = Transaction.objects.filter(
            return_date__isnull=True,
            due_date__lt=now
        )
        
        # Update status to overdue
        transactions.update(status='overdue')
        
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class FineView(APIView):
    """
    API endpoint for fine management.
    
    GET /api/fines/ - Get fine summary for a user
    POST /api/fines/pay/ - Pay a fine
    GET /api/fines/report/ - Get overdue items report (admin)
    """
    
    def get(self, request):
        """Get fine summary for a user."""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_id = int(user_id)
        except ValueError:
            return Response(
                {'error': 'user_id must be an integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report = FineReport()
        summary = report.get_user_fine_summary(user_id)
        
        return Response(summary)


class FinePaymentView(APIView):
    """API endpoint for paying fines."""
    
    def post(self, request):
        """Process a fine payment."""
        serializer = FinePaymentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        calculator = FineCalculator()
        result = calculator.pay_fine(
            serializer.validated_data['transaction_id'],
            serializer.validated_data['amount']
        )
        
        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class OverdueReportView(APIView):
    """API endpoint for overdue items report."""
    
    def get(self, request):
        """Get report of all overdue items."""
        report = FineReport()
        overdue_items = report.get_overdue_items_report()
        
        return Response({
            'count': len(overdue_items),
            'generated_at': timezone.now().isoformat(),
            'items': overdue_items
        })


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserProfile CRUD operations.
    
    Provides:
    - GET /api/users/ - List all user profiles
    - POST /api/users/ - Create new user with profile
    - GET /api/users/{id}/ - Get user profile details
    - PUT /api/users/{id}/ - Update user profile
    - GET /api/users/{id}/transactions/ - Get user's transactions
    - GET /api/users/{id}/fines/ - Get user's fine summary
    """
    
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get all transactions for a user."""
        profile = self.get_object()
        transactions = Transaction.objects.filter(user=profile.user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def fines(self, request, pk=None):
        """Get fine summary for a user."""
        profile = self.get_object()
        report = FineReport()
        summary = report.get_user_fine_summary(profile.user.id)
        return Response(summary)
    
    @action(detail=True, methods=['get'])
    def active_checkouts(self, request, pk=None):
        """Get active checkouts for a user."""
        profile = self.get_object()
        transactions = Transaction.objects.filter(
            user=profile.user,
            status__in=['checked_out', 'overdue']
        )
        serializer = TransactionSerializer(transactions, many=True)
        return Response({
            'count': transactions.count(),
            'max_allowed': profile.max_items_allowed,
            'can_checkout_more': profile.can_checkout_more(),
            'transactions': serializer.data
        })


# Health check endpoint
@api_view(['GET'])
def health_check(request):
    """Simple health check endpoint."""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'service': 'Library Management System API'
    })
