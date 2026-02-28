#!/usr/bin/env python
"""Quick API endpoint testing script"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.catalog.models import Book, DVD, EBook
from apps.loans.models import Loan
from apps.loans.services import LoanService

User = get_user_model()

print("🚀 Creating test data...")

# Create users
admin, _ = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@library.com', 'role': User.Role.LIBRARIAN}
)
if not admin.has_usable_password():
    admin.set_password('admin123')
    admin.save()

member, _ = User.objects.get_or_create(
    username='alice',
    defaults={'email': 'alice@example.com', 'role': User.Role.MEMBER}
)
if not member.has_usable_password():
    member.set_password('password123')
    member.save()

print(f"✓ Users: {User.objects.count()} total")

# Create books
if Book.objects.count() == 0:
    Book.objects.create(
        title="Clean Code",
        author="Robert C. Martin",
        isbn="9780132350884",
        publication_year=2008,
    )
    Book.objects.create(
        title="The Pragmatic Programmer",
        author="Andrew Hunt",
        isbn="9780135957059",
        publication_year=2019,
    )
    Book.objects.create(
        title="Design Patterns",
        author="Gang of Four",
        isbn="9780201633610",
        publication_year=1994,
    )

print(f"✓ Books: {Book.objects.count()}")

# Create DVDs
if DVD.objects.count() == 0:
    DVD.objects.create(
        title="Inception",
        director="Christopher Nolan",
        runtime_minutes=148,
        release_year=2010,
    )
    DVD.objects.create(
        title="The Matrix",
        director="The Wachowskis",
        runtime_minutes=136,
        release_year=1999,
    )

print(f"✓ DVDs: {DVD.objects.count()}")

# Create eBooks
if EBook.objects.count() == 0:
    EBook.objects.create(
        title="Python Crash Course",
        author="Eric Matthes",
        publication_year=2019,
        file_size_mb=5.2,
        file_format=EBook.Format.EPUB,
        total_licenses=3,
    )

print(f"✓ eBooks: {EBook.objects.count()}")

print(f"\n📚 Total library items: {Book.objects.count() + DVD.objects.count() + EBook.objects.count()}")
print(f"👥 Total users: {User.objects.count()}")
print(f"📋 Total loans: {Loan.objects.count()}")

print("\n✅ Test data created successfully!")
print("\n📋 Credentials:")
print("   Admin: admin / admin123")
print("   Member: alice / password123")
