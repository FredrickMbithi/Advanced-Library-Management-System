"""
Admin configuration for loans app.
"""

from django.contrib import admin
from apps.loans.models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('item', 'borrower', 'borrowed_at', 'due_at', 'returned_at', 'is_overdue')
    list_filter = ('returned_at', 'borrowed_at', 'due_at')
    search_fields = ('item__title', 'borrower__username')
    readonly_fields = ('borrowed_at',)
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
