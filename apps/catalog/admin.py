"""
Admin configuration for catalog app.
"""

from django.contrib import admin
from apps.catalog.models import LibraryItem, Book, DVD, EBook


@admin.register(LibraryItem)
class LibraryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'item_type', 'is_available', 'created_at')
    list_filter = ('item_type', 'is_available')
    search_fields = ('title',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'publication_year', 'is_available')
    list_filter = ('is_available', 'publication_year')
    search_fields = ('title', 'author', 'isbn')


@admin.register(DVD)
class DVDAdmin(admin.ModelAdmin):
    list_display = ('title', 'director', 'runtime_minutes', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('title', 'director')


@admin.register(EBook)
class EBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'file_size_mb', 'total_licenses', 'active_loans_count')
    list_filter = ('total_licenses',)
    search_fields = ('title', 'author')
