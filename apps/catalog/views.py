from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from apps.catalog.models import LibraryItem, Book, DVD, EBook
from apps.catalog.serializers import (
    BookSerializer, DVDSerializer, EBookSerializer,
    PolymorphicLibraryItemSerializer,
)
from apps.catalog.filters import LibraryItemFilter, BookFilter, DVDFilter, EBookFilter
from apps.accounts.permissions import IsLibrarianOrReadOnly


class LibraryItemListView(generics.ListAPIView):
    """
    GET /items/
    Filtering: item_type, is_available, title (icontains)
    Search: title
    Order: title, created_at
    """
    queryset = LibraryItem.objects.all()
    serializer_class = PolymorphicLibraryItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LibraryItemFilter
    search_fields = ["title"]
    ordering_fields = ["title", "created_at", "is_available"]
    ordering = ["title"]


class BookListCreateView(generics.ListCreateAPIView):
    """
    GET  /books/ — filter, search, order
    POST /books/ — librarian only

    Search: title, author
    Filter: author, publication_year, is_available
    Order:  title, publication_year, is_available
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsLibrarianOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookFilter
    search_fields = ["title", "author"]
    ordering_fields = ["title", "publication_year", "is_available"]
    ordering = ["title"]


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsLibrarianOrReadOnly]


class DVDListCreateView(generics.ListCreateAPIView):
    queryset = DVD.objects.all()
    serializer_class = DVDSerializer
    permission_classes = [IsLibrarianOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DVDFilter
    search_fields = ["title", "director"]
    ordering_fields = ["title", "release_year", "is_available"]
    ordering = ["title"]


class DVDDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DVD.objects.all()
    serializer_class = DVDSerializer
    permission_classes = [IsLibrarianOrReadOnly]


class EBookListCreateView(generics.ListCreateAPIView):
    queryset = EBook.objects.all()
    serializer_class = EBookSerializer
    permission_classes = [IsLibrarianOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EBookFilter
    search_fields = ["title", "author"]
    ordering_fields = ["title", "publication_year", "is_available"]
    ordering = ["title"]


class EBookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EBook.objects.all()
    serializer_class = EBookSerializer
    permission_classes = [IsLibrarianOrReadOnly]
