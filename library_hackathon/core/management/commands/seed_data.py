"""
Management command to seed the database with initial library items.

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear  # Clear existing data first
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from core.models import LibraryItem, UserProfile


class Command(BaseCommand):
    help = 'Seed the database with initial library items from library_items.json'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing library items before seeding',
        )
        parser.add_argument(
            '--create-users',
            action='store_true',
            help='Also create sample users for testing',
        )
    
    def handle(self, *args, **options):
        # Find the data file
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        data_file = base_dir / 'data' / 'library_items.json'
        
        if not data_file.exists():
            raise CommandError(f'Data file not found: {data_file}')
        
        # Clear existing items if requested
        if options['clear']:
            self.stdout.write('Clearing existing library items...')
            LibraryItem.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing items'))
        
        # Load and parse the JSON file
        self.stdout.write(f'Loading data from {data_file}...')
        with open(data_file, 'r') as f:
            items_data = json.load(f)
        
        # Create library items
        created_count = 0
        for item_data in items_data:
            item = self._create_library_item(item_data)
            if item:
                created_count += 1
                self.stdout.write(f'  Created: {item}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} library items')
        )
        
        # Create sample users if requested
        if options['create_users']:
            self._create_sample_users()
    
    def _create_library_item(self, data: dict) -> LibraryItem:
        """Create a LibraryItem from dictionary data."""
        item_type = data.get('item_type', 'book')
        
        # Determine if digital based on type
        is_digital = item_type in ['ebook', 'audiobook']
        
        item = LibraryItem.objects.create(
            title=data.get('title', ''),
            author=data.get('author', ''),
            year_published=data.get('year_published', 0),
            genre=data.get('genre', ''),
            item_type=item_type,
            location=data.get('location', 'General Section'),
            is_available=True,
            is_digital=is_digital,
            
            # Book fields
            isbn=data.get('isbn', ''),
            pages=data.get('pages', 0),
            edition=data.get('edition', ''),
            
            # DVD fields
            runtime_minutes=data.get('runtime_minutes', 0),
            rating=data.get('rating', ''),
            director=data.get('director', ''),
            
            # Magazine fields
            issue_number=data.get('issue_number', ''),
            issue_date=data.get('issue_date', ''),
            publisher=data.get('publisher', ''),
            
            # Digital fields
            file_format=data.get('file_format', ''),
            file_size_mb=data.get('file_size_mb', 0.0),
            concurrent_access_limit=data.get('concurrent_access_limit', 1),
            drm_protected=data.get('drm_protected', False),
            
            # AudioBook fields
            narrator=data.get('narrator', ''),
            duration_hours=data.get('duration_hours', 0.0),
            chapters=data.get('chapters', 0),
        )
        
        return item
    
    def _create_sample_users(self):
        """Create sample users for testing."""
        self.stdout.write('Creating sample users...')
        
        sample_users = [
            {
                'username': 'alice',
                'email': 'alice@library.com',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'membership_type': 'premium',
                'max_items': 10,
            },
            {
                'username': 'bob',
                'email': 'bob@library.com',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'membership_type': 'basic',
                'max_items': 5,
            },
            {
                'username': 'charlie',
                'email': 'charlie@library.com',
                'first_name': 'Charlie',
                'last_name': 'Brown',
                'membership_type': 'student',
                'max_items': 7,
            },
        ]
        
        for user_data in sample_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                
                UserProfile.objects.create(
                    user=user,
                    membership_type=user_data['membership_type'],
                    max_items_allowed=user_data['max_items'],
                )
                
                self.stdout.write(f'  Created user: {user.username}')
            else:
                self.stdout.write(f'  User already exists: {user.username}')
        
        self.stdout.write(self.style.SUCCESS('Sample users created'))
