# Advanced Library Management System

A sophisticated Django REST Framework application for managing library operations including book cataloging, loans, user management, and fine calculations.

## 🚀 Features

### 📚 Multi-Type Item Catalog

- **Books**: Physical books with ISBN, author, publication year
- **DVDs**: Physical media with director, duration, release date
- **E-Books**: Digital content with file size and license management
- Polymorphic item handling with shared base model
- Availability tracking across all item types

### 👥 User Management

- Custom user model with role-based access (Member/Librarian)
- Permission system for librarian-only operations
- User authentication and authorization via DRF

### 📖 Loan Management

- Borrow and return workflow
- Automatic due date calculation based on item type
- Overdue detection (state-based, not stored)
- Fine calculation service ($1/day overdue)
- User blocking when fines exceed $10
- Complete loan history tracking

### 🔍 Advanced Filtering & Search

- Filter items by type, availability, author, year
- Full-text search on titles and authors
- Ordering by multiple fields
- DRF integration with django-filter

### 🛡️ Best Practices

- Domain-Driven Design principles
- Service layer for business logic
- State machines for loan lifecycle
- Comprehensive test coverage
- RESTful API design

## 📁 Project Structure

```
library_system/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
│
├── library_system/              # Project configuration
│   ├── __init__.py
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Main URL configuration
│   └── wsgi.py                 # WSGI application
│
└── apps/                        # Django applications
    │
    ├── accounts/                # User management
    │   ├── models.py           # Custom User model with roles
    │   ├── permissions.py      # Custom permission classes
    │   ├── admin.py            # Admin configuration
    │   └── apps.py
    │
    ├── catalog/                 # Item catalog
    │   ├── models/
    │   │   ├── __init__.py     # Model exports
    │   │   ├── base.py         # LibraryItem base model
    │   │   ├── physical.py     # Book, DVD models
    │   │   └── digital.py      # EBook model
    │   ├── views.py            # API views
    │   ├── serializers.py      # DRF serializers
    │   ├── filters.py          # Django-filter classes
    │   ├── urls.py             # URL routing
    │   ├── admin.py            # Admin configuration
    │   └── apps.py
    │
    └── loans/                   # Loan management
        ├── models.py           # Loan model
        ├── services.py         # Business logic (FineCalculator, LoanService)
        ├── views.py            # API views
        ├── serializers.py      # DRF serializers
        ├── urls.py             # URL routing
        ├── tests.py            # Comprehensive test suite
        ├── admin.py            # Admin configuration
        └── apps.py
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- pip and virtualenv
- PostgreSQL (for production) or SQLite (development)

### Step 1: Clone and Setup Virtual Environment

```bash
cd "/home/ghost/Advanced Library Management System"

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
# Minimum required: SECRET_KEY
nano .env  # or use your preferred editor
```

### Step 4: Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### Step 5: Run Development Server

```bash
python manage.py runserver
```

Visit:

- **API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/

## 📡 API Endpoints

### Catalog Endpoints

```
GET    /api/catalog/items/              # List all items (polymorphic)
GET    /api/catalog/books/              # List books
POST   /api/catalog/books/              # Create book (librarian only)
GET    /api/catalog/books/{id}/         # Retrieve book details
PUT    /api/catalog/books/{id}/         # Update book (librarian only)
DELETE /api/catalog/books/{id}/         # Delete book (librarian only)

GET    /api/catalog/dvds/               # List DVDs
POST   /api/catalog/dvds/               # Create DVD (librarian only)
...

GET    /api/catalog/ebooks/             # List E-Books
POST   /api/catalog/ebooks/             # Create E-Book (librarian only)
...
```

### Loan Endpoints

```
GET    /api/loans/                      # List all loans
POST   /api/loans/borrow/               # Borrow an item
POST   /api/loans/{id}/return/          # Return an item
GET    /api/loans/my-loans/             # Current user's active loans
```

### Query Parameters

**Filtering** (on list endpoints):

```
?item_type=BOOK                          # Filter by type
?is_available=true                       # Available items only
?author=Robert%20Martin                  # Filter by author (books)
?publication_year=2008                   # Filter by year
```

**Search**:

```
?search=Clean%20Code                     # Search in title/author
```

**Ordering**:

```
?ordering=title                          # Order by title
?ordering=-publication_year              # Reverse order by year
```

## 🧪 Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test apps.loans

# Run with coverage (install coverage first: pip install coverage)
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## 🏗️ Key Design Decisions

### 1. Concrete Base Model

- `LibraryItem` is a concrete model (not abstract)
- Allows `Loan.item = FK(LibraryItem)` to work for all item types
- Enables polymorphic queries across all items

### 2. State-Based Loan Lifecycle

- No `status` field - state is derived from timestamps
- `returned_at=None` → Active loan
- `returned_at` set → Returned loan
- Prevents state drift and invalid transitions

### 3. Service Layer Pattern

- `FineCalculator`: Stateless fine computation service
- `LoanService`: Handles borrow/return business logic
- Keeps models lean, views thin, and logic testable

### 4. Fine Calculation

- Fines are NOT stored in the database
- Computed on-demand from loan dates
- $1.00 per day overdue
- $10.00 threshold blocks borrowing

## 🔐 Permissions

- **Public**: Read-only access to catalog
- **Members**: Can borrow/return items, view own loans
- **Librarians**: Full CRUD on catalog, view all loans

## 🗄️ Database Models

### LibraryItem (Base)

- `title`: CharField
- `item_type`: Choice field (BOOK, DVD, EBOOK)
- `is_available`: Boolean
- `created_at`, `updated_at`: Timestamps

### Book (extends LibraryItem)

- `author`, `isbn`, `publisher`
- `publication_year`
- `loan_period_days`

### DVD (extends LibraryItem)

- `director`, `duration_minutes`
- `release_date`
- `loan_period_days`

### EBook (extends LibraryItem)

- `author`, `file_size_mb`
- `download_link`
- `total_licenses`, `available_licenses`

### User (Custom)

- Extends Django's `AbstractUser`
- `role`: MEMBER or LIBRARIAN

### Loan

- `item`: FK to LibraryItem
- `borrower`: FK to User
- `borrowed_at`, `due_at`, `returned_at`

## 📦 Dependencies

- **Django** 4.2+: Web framework
- **djangorestframework** 3.14+: REST API
- **django-filter** 23.0+: Advanced filtering
- **python-decouple** 3.8+: Environment configuration
- **psycopg2-binary** 2.9+: PostgreSQL adapter (production)

## 🚧 Development Roadmap

### Immediate Next Steps

1. ✅ Organize project structure
2. ✅ Create comprehensive documentation
3. ⏳ Run initial migrations
4. ⏳ Load sample data (fixtures)
5. ⏳ Test all API endpoints

### Future Enhancements

- [ ] Add reservation system for checked-out items
- [ ] Email notifications for due dates
- [ ] Late fee payment tracking
- [ ] Book recommendations system
- [ ] Multi-branch library support
- [ ] Report generation (most borrowed, overdue stats)
- [ ] JWT authentication
- [ ] API rate limiting
- [ ] Celery for async tasks
- [ ] Docker deployment configuration

## 🤝 Contributing

1. Create a feature branch
2. Write tests for new features
3. Ensure all tests pass
4. Follow Django and PEP 8 style guidelines
5. Submit pull request with clear description

## 📄 License

This project is for educational purposes. Adapt as needed for your use case.

## 📧 Support

For issues or questions, please create an issue in the repository.

---

**Built with Django REST Framework** 🎯
