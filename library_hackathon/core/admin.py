"""
core/admin.py - Django Admin Configuration

Register models with the Django admin site for easy management.
"""

from django.contrib import admin
from .models import LibraryItem, Transaction, UserProfile


@admin.register(LibraryItem)
class LibraryItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'item_type', 'is_available', 'is_digital']
    list_filter = ['item_type', 'is_available', 'is_digital', 'genre']
    search_fields = ['title', 'author', 'isbn']
    ordering = ['title']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'year_published', 'genre', 'item_type')
        }),
        ('Availability', {
            'fields': ('location', 'is_available', 'is_digital')
        }),
        ('Book Details', {
            'fields': ('isbn', 'pages', 'edition'),
            'classes': ('collapse',)
        }),
        ('DVD Details', {
            'fields': ('runtime_minutes', 'rating', 'director'),
            'classes': ('collapse',)
        }),
        ('Magazine Details', {
            'fields': ('issue_number', 'issue_date', 'publisher'),
            'classes': ('collapse',)
        }),
        ('Digital Details', {
            'fields': ('file_format', 'file_size_mb', 'concurrent_access_limit', 'drm_protected'),
            'classes': ('collapse',)
        }),
        ('AudioBook Details', {
            'fields': ('narrator', 'duration_hours', 'chapters'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'library_item', 'checkout_date', 'due_date', 'status', 'fine_amount']
    list_filter = ['status', 'fine_paid']
    search_fields = ['user__username', 'library_item__title']
    date_hierarchy = 'checkout_date'
    ordering = ['-checkout_date']
    
    readonly_fields = ['checkout_date', 'created_at', 'updated_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'membership_type', 'max_items_allowed', 'membership_start']
    list_filter = ['membership_type']
    search_fields = ['user__username', 'user__email']
