from django.urls import path
from apps.catalog.views import (
    LibraryItemListView,
    BookListCreateView, BookDetailView,
    DVDListCreateView, DVDDetailView,
    EBookListCreateView, EBookDetailView,
)

app_name = 'catalog'

urlpatterns = [
    # Unified item view
    path("items/", LibraryItemListView.as_view(), name="item-list"),

    # Type-specific catalog endpoints
    path("books/", BookListCreateView.as_view(), name="book-list-create"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="book-detail"),

    path("dvds/", DVDListCreateView.as_view(), name="dvd-list-create"),
    path("dvds/<int:pk>/", DVDDetailView.as_view(), name="dvd-detail"),

    path("ebooks/", EBookListCreateView.as_view(), name="ebook-list-create"),
    path("ebooks/<int:pk>/", EBookDetailView.as_view(), name="ebook-detail"),
]
