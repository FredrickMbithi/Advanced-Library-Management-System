# Library Management System

**Author:** Fredrick Mbithi  
**License:** MIT

A production-grade Django REST Framework application demonstrating domain-driven design principles in a library management context. This system handles multi-type catalog management, loan workflows, fine calculations, and role-based access control with an emphasis on clean architecture and business logic encapsulation.

> **⚠️ Educational Project Notice**: While this project follows production best practices, review [SECURITY.md](SECURITY.md) before deploying to production environments.

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Core Features](#core-features)
- [Design Philosophy](#design-philosophy)
- [Technical Stack](#technical-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Key Design Decisions](#key-design-decisions)
- [Testing Strategy](#testing-strategy)
- [API Documentation](#api-documentation)
- [Development Process](#development-process)
- [Additional Documentation](#additional-documentation)

---

## 🏛️ Architecture Overview

This system is built around **Domain-Driven Design (DDD)** principles with a clear separation between business logic and infrastructure concerns. The architecture consists of three primary bounded contexts:

### Bounded Contexts

1. **Catalog Context** (`apps/catalog/`)
   - Manages library inventory across multiple item types
   - Implements polymorphic inheritance for Books, DVDs, and E-Books
   - Handles availability state transitions at the domain level

2. **Accounts Context** (`apps/accounts/`)
   - Custom User model with domain-specific roles (Member/Librarian)
   - Permission abstractions for librarian-only operations
   - Encapsulates borrowing eligibility rules

3. **Loans Context** (`apps/loans/`)
   - Manages the complete loan lifecycle
   - Pure domain services for fine calculation
   - State-based loan status (avoiding antipatterns)

### Layered Architecture

```
┌─────────────────────────────────────┐
│   REST API Layer (Views)            │  ← HTTP, Serialization, Auth
├─────────────────────────────────────┤
│   Service Layer                     │  ← Business Logic, Transactions
├─────────────────────────────────────┤
│   Domain Model Layer                │  ← Entities, Value Objects, State
├─────────────────────────────────────┤
│   Data Access Layer (ORM)           │  ← Django Models, QuerySets
└─────────────────────────────────────┘
```

**Why this structure?**

- Business rules remain testable without HTTP/database overhead
- Views orchestrate, they don't implement domain logic
- Services handle cross-aggregate transactions and complex workflows
- Models own their state transitions and invariants

---

## 🚀 Core Features

### 📚 Polymorphic Catalog System

The catalog implements **multi-table inheritance** with a concrete base class:

- **Books**: ISBN, author, publisher, page count, physical condition
- **DVDs**: Director, runtime, release year, physical condition
- **E-Books**: File size, format, license pool management

**Why concrete inheritance?**

- Enables unified queries across all item types via `LibraryItem.objects.all()`
- Foreign keys from `Loan` reference the base table, avoiding discriminator fields
- Subclass-specific fields remain isolated (no sparse column antipattern)

### 👥 Role-Based Access Control

Custom `User` model with domain-specific roles:

- **Members**: Can borrow items (subject to fine threshold), view own loans
- **Librarians**: Full access to all operations and user management

Permissions are implemented as **reusable DRF permission classes**, not hardcoded checks in views.

### 📖 State-Based Loan Lifecycle

Loans use **derived state** rather than storing status fields:

```python
# State is computed from timestamps, never stored
@property
def is_overdue(self) -> bool:
    return self.is_active and timezone.now() > self.due_at
```

**What this avoids:**

- Status field drift (e.g., status="ACTIVE" but returned_at is set)
- Update anomalies when changing state
- Need for database migrations when adding new states

### 💰 Fine Calculation Service

Fines are computed on-demand by a **stateless domain service**:

```python
class FineCalculator:
    rate_per_day: Decimal = Decimal("1.00")

    @classmethod
    def compute(cls, loan) -> Decimal:
        if not loan.is_overdue:
            return Decimal("0.00")
        return Decimal(loan.days_overdue) * cls.rate_per_day
```

**Why not store fines in the database?**

- Fines are temporal – they increase every day
- Storing fines creates stale data
- Calculation is cheap and policy can be changed retroactively
- Subclassing allows different rate policies (student discounts, etc.)

### 🔍 Advanced Filtering & Search

- Django-filter integration for declarative filtering
- Full-text search on titles and authors
- Availability filtering with database indexes
- Composite filters (e.g., available books by author from year X)

---

## 🧠 Design Philosophy

### Core Principles

1. **Domain First**: Business rules live in models and services, not views
2. **State Integrity**: Use database constraints and derived properties over status fields
3. **Separation of Concerns**: Views handle HTTP, services handle workflows, models handle invariants
4. **Testability**: Business logic is unit-testable without HTTP/database mocking
5. **Explicit Over Implicit**: Method names like `mark_checked_out()` vs `update(is_available=False)`

### Trade-offs and Constraints

**Multi-Table Inheritance vs Single Table**

- **Chosen**: Multi-table inheritance
- **Rationale**: Avoids sparse columns, maintains referential integrity, cleaner schema
- **Cost**: Additional JOINs for subclass queries (mitigated with `select_related`)

**Service Layer vs Fat Models**

- **Chosen**: Service layer for cross-aggregate workflows
- **Rationale**: Loan creation requires Item + User + Loan coordination
- **Cost**: Additional abstraction layer (justified by testability)

**Computed Fines vs Stored Fines**

- **Chosen**: Computed on-demand
- **Rationale**: Temporal data, policy flexibility, no staleness
- **Cost**: Computation on every query (mitigated by efficient SQL)

---

## 🛠️ Technical Stack

### Backend

- **Django 4.2**: Web framework
- **Django REST Framework 3.14**: API layer, serialization, permissions
- **Django-filter 23.0**: Declarative filtering for querysets
- **Python-decouple 3.8**: Environment-based configuration

### Database

- **SQLite** (development): Zero-config, file-based
- **PostgreSQL** (recommended for production): ACID compliance, advanced indexing

### Development Tools

- **Python 3.10+**: Type hints, dataclasses, modern syntax
- **Django Test Framework**: Unit and integration testing
- **DRF Test Client**: API endpoint testing

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip and virtualenv

### Installation

```bash
# Clone the repository
cd library-management-system

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" >> .env

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata sample_data.json

# Start development server
python manage.py runserver
```

### Verify Installation

```bash
# Run test suite
python manage.py test

# Access the API
curl http://localhost:8000/api/catalog/items/

# Access admin panel
open http://localhost:8000/admin/
```

For detailed setup instructions, see [GETTING_STARTED.md](GETTING_STARTED.md).

---

## 📁 Project Structure

```
library-management-system/
├── apps/
│   ├── accounts/          # User management, roles, permissions
│   │   ├── models.py      # Custom User with domain-specific roles
│   │   ├── permissions.py # Reusable DRF permission classes
│   │   ├── serializers.py # User registration, profile serialization
│   │   └── views.py       # Registration, user list endpoints
│   │
│   ├── catalog/           # Item inventory management
│   │   ├── models/
│   │   │   ├── base.py    # LibraryItem (concrete base class)
│   │   │   ├── physical.py # Book, DVD (multi-table inheritance)
│   │   │   └── digital.py  # EBook (license pooling)
│   │   ├── filters.py     # Django-filter configurations
│   │   ├── serializers.py # Polymorphic serialization
│   │   └── views.py       # CRUD viewsets for items
│   │
│   └── loans/             # Loan lifecycle management
│       ├── models.py      # Loan (state-based, no status field)
│       ├── services.py    # LoanService, FineCalculator (domain services)
│       ├── serializers.py # Loan creation, return validation
│       └── views.py       # Checkout, return, loan history endpoints
│
├── library_system/        # Project configuration
│   ├── settings.py       # Django settings (env-based config)
│   ├── urls.py           # Root URL configuration
│   └── wsgi.py           # WSGI entry point
│
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
├── db.sqlite3            # SQLite database (development)
└── demo.sh               # Interactive demo script
```

### Why Three Apps?

Each app represents a **bounded context** in DDD terms:

- **Accounts**: Identity and access
- **Catalog**: Inventory domain
- **Loans**: Borrowing lifecycle

Cross-context communication happens through:

- Foreign keys to stable interfaces (e.g., `Loan.borrower → User`)
- Service layer orchestration (e.g., `LoanService` coordinates Item + User + Loan)

---

## 🔑 Key Design Decisions

### 1. Concrete Base Class for Polymorphism

**Implementation:**

```python
class LibraryItem(models.Model):
    title = models.CharField(max_length=255)
    item_type = models.CharField(max_length=10, choices=ItemType.choices)
    is_available = models.BooleanField(default=True)
    # Subclasses: Book, DVD, EBook

class Loan(models.Model):
    item = models.ForeignKey(LibraryItem, on_delete=models.PROTECT)
```

**Rationale:**

- Enables `Loan.item` to reference any catalog item type
- Unified queries: `LibraryItem.objects.filter(is_available=True)`
- Type-safe navigation: `item.book`, `item.dvd`, `item.ebook`

**Alternative Considered:** Abstract base class

- **Rejected because:** Foreign keys can't reference abstract models

### 2. State-Based Loan Status

**Implementation:**

```python
@property
def is_overdue(self) -> bool:
    return self.returned_at is None and timezone.now() > self.due_at
```

**Rationale:**

- **Single source of truth**: Timestamps determine state, not redundant status fields
- **Atomicity**: Can't have status="ACTIVE" with returned_at set
- **Future-proof**: Adding new states (e.g., "RESERVED") doesn't require migrations

**Alternative Considered:** `status = models.CharField(choices=LoanStatus.choices)`

- **Rejected because:** Status drift (update anomalies when state changes)

### 3. Service Layer for Checkout/Return

**Implementation:**

```python
class LoanService:
    @staticmethod
    def checkout_item(item, borrower):
        # Validates eligibility (fines, availability)
        # Creates loan with computed due date
        # Marks item unavailable
        # All within a transaction
```

**Rationale:**

- **Transaction boundary**: Checkout requires coordinated writes to Item + Loan
- **Testability**: Business logic is unit-testable without HTTP layer
- **Reusability**: Service can be called from views, management commands, or background jobs

**Alternative Considered:** Fat models with `item.checkout(user)`

- **Rejected because:** Cross-aggregate coordination doesn't belong in a single model

### 4. Fine Calculation as Pure Service

**Implementation:**

```python
class FineCalculator:
    @classmethod
    def compute(cls, loan) -> Decimal:
        if not loan.is_overdue:
            return Decimal("0.00")
        return Decimal(loan.days_overdue) * cls.rate_per_day
```

**Rationale:**

- **Temporal correctness**: Fines increase daily; storing them creates stale data
- **Policy flexibility**: Rate can be changed without migrating historical data
- **Subclass-friendly**: Different rate policies (student, faculty) via inheritance

**Alternative Considered:** `Loan.fine_amount = models.DecimalField()`

- **Rejected because:** Would require daily batch updates to keep correct

### 5. Database Constraints for Invariants

**Implementation:**

```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=["item", "borrower"],
            condition=models.Q(returned_at__isnull=True),
            name="unique_active_loan_per_item_borrower"
        )
    ]
```

**Rationale:**

- **Defense in depth**: Application logic can have bugs, database enforces invariants
- **Concurrency safety**: Prevents race conditions in checkout flow
- **Self-documenting**: Constraint names explain business rules

---

## 🧪 Testing Strategy

### Coverage Overview

- **50+ tests** across all modules
- **100% pass rate**
- Unit tests for domain logic (models, services)
- Integration tests for API endpoints
- Edge case coverage (overdue loans, fine thresholds, permissions)

### Test Organization

```
apps/
├── accounts/tests.py       # User model, registration, permissions
├── catalog/tests.py        # Item models, polymorphism, state transitions
└── loans/tests.py          # Loan lifecycle, fine calculations, API workflows
```

### Testing Approach

**Unit Tests (Domain Layer):**

```python
class FineCalculatorTests(TestCase):
    def test_fine_is_one_dollar_per_day(self):
        loan = self._make_overdue_loan(days_overdue=5)
        self.assertEqual(FineCalculator.compute(loan), Decimal("5.00"))
```

- Fast, no database/HTTP overhead
- Tests business rules in isolation

**Integration Tests (API Layer):**

```python
class LoanCheckoutTests(APITestCase):
    def test_member_can_checkout_available_book(self):
        response = self.client.post('/api/loans/checkout/',
                                    data={'item_id': self.book.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

- Tests full request/response cycle
- Validates serialization, permissions, and business logic integration

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.loans

# Run with coverage report
coverage run --source='.' manage.py test
coverage report
```

**Why comprehensive testing?**

- Domain logic correctness is critical (fines, availability)
- Refactoring confidence
- Documentation of expected behavior
- Regression prevention

---

## 📡 API Documentation

### Authentication

The API uses **HTTP Basic Authentication** for development. For production, implement JWT or OAuth2.

```bash
curl --user username:password http://localhost:8000/api/loans/
```

### Core Endpoints

**Catalog Management:**

```
GET    /api/catalog/items/              # List all items (polymorphic)
GET    /api/catalog/books/              # List books
GET    /api/catalog/books/{id}/         # Get book details
POST   /api/catalog/books/              # Create book (librarian only)
PUT    /api/catalog/books/{id}/         # Update book (librarian only)
DELETE /api/catalog/books/{id}/         # Delete book (librarian only)
```

**User Management:**

```
POST   /api/users/register/             # Register new user
GET    /api/users/                      # List users (librarian only)
GET    /api/users/{id}/                 # Get user profile
```

**Loan Operations:**

```
GET    /api/loans/                      # List loans (own or all if librarian)
POST   /api/loans/checkout/             # Checkout an item
POST   /api/loans/{id}/return/          # Return an item
GET    /api/users/{id}/fines/           # View user fines
```

### Filtering and Search

**Filter by availability:**

```bash
GET /api/catalog/books/?is_available=true
```

**Search by title or author:**

```bash
GET /api/catalog/books/?search=Clean+Code
```

**Filter by year:**

```bash
GET /api/catalog/books/?publication_year=2008
```

For complete API examples with curl commands, see [API_EXAMPLES.md](API_EXAMPLES.md).

---

## 🔧 Development Process

This project was architected and implemented by **Fredrick Mbithi** following industry best practices for backend systems. The development process emphasized:

- **Domain modeling first**: Understanding library operations before writing code
- **Iterative refinement**: Moving from simple CRUD to domain-driven architecture
- **Test-driven validation**: Writing tests alongside features to ensure correctness
- **Documentation as code**: Keeping README and inline documentation synchronized

### On AI-Assisted Development

AI tools (including GitHub Copilot and Claude) were used as **assistants** during development, primarily for:

- Boilerplate generation (serializers, basic CRUD views)
- Documentation drafting and refinement
- Test case generation suggestions

However, all architectural decisions, design patterns, and domain modeling were conceived and validated by the author. The AI tools served as productivity multipliers, not as architects or decision-makers.

### Development Philosophy

> "Make it work, make it right, make it fast."  
> – Kent Beck

This project prioritizes **"make it right"** by emphasizing clean architecture and explicit business rules over premature optimization. Performance concerns are addressed through selective use of:

- Database indexes on foreign keys and filter fields
- `select_related()` for reducing N+1 queries
- Computed properties for temporal data instead of cached values

---

## 📚 Additional Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** – Step-by-step setup guide
- **[API_EXAMPLES.md](API_EXAMPLES.md)** – Complete API reference with curl examples
- **[SECURITY.md](SECURITY.md)** – Security considerations for production deployment
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** – Current feature status and roadmap
- **[CONTRIBUTING.md](CONTRIBUTING.md)** – Guidelines for contributors

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Django Software Foundation for the excellent web framework
- DRF community for the comprehensive REST toolkit
- The clean code and domain-driven design communities for architectural inspiration

---

**Built by Fredrick Mbithi with Django REST Framework** 🎯
