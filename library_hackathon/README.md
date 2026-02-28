# Advanced Library Management System

A professional, scalable library management system built with Django REST Framework. This system demonstrates clean architecture principles by separating Web API logic from core business logic using object-oriented design patterns.

## Features

- **Item Management**: Support for multiple item types (Books, DVDs, Magazines, EBooks, AudioBooks)
- **Checkout/Return System**: Complete transaction management with availability tracking
- **Fine Calculation**: Automated fine computation with configurable rates
- **User Profiles**: Membership management with checkout limits
- **RESTful API**: Full CRUD operations with Django REST Framework

## Architecture

```
library_hackathon/
├── core/
│   ├── logic/
│   │   ├── base.py          # Abstract base classes and interfaces
│   │   ├── items.py         # Item type implementations (Polymorphism)
│   │   └── calculator.py    # Fine calculation service (Encapsulation)
│   ├── models.py            # Django ORM models
│   ├── serializers.py       # DRF serializers for validation
│   ├── views.py             # API endpoints
│   └── urls.py              # URL routing
├── data/
│   └── library_items.json   # Seed data
└── library_hackathon/
    └── settings.py          # Django configuration
```

## Design Patterns

### Abstraction
Abstract base classes define contracts for library items using Python's `abc` module. The `AbstractBaseItem` class enforces implementation of core methods like `is_digital()` and `get_loan_period_days()`.

### Polymorphism
Different item types override behavior appropriately:
- **Book**: 14-day loan period
- **DVD**: 7-day loan period
- **Magazine**: 7-day loan period
- **EBook**: 21-day access period
- **AudioBook**: 14-day access period

### Encapsulation
Fine calculation logic is encapsulated in the `FineCalculator` service class:

```
Fine = max(0, (return_date - due_date).days × daily_rate)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health/` | GET | Service health check |
| `/api/items/` | GET | List all library items |
| `/api/items/{id}/` | GET | Get item details |
| `/api/items/available/` | GET | List available items |
| `/api/items/search/?q={query}` | GET | Search items |
| `/api/checkout/` | POST | Checkout an item |
| `/api/return/` | POST | Return an item |
| `/api/transactions/` | GET | List all transactions |
| `/api/transactions/active/` | GET | List active checkouts |
| `/api/transactions/overdue/` | GET | List overdue items |
| `/api/fines/?user_id={id}` | GET | Get user fine summary |
| `/api/fines/pay/` | POST | Process fine payment |
| `/api/users/` | GET | List user profiles |
| `/api/users/{id}/active_checkouts/` | GET | Get user's active checkouts |

## Installation

### Prerequisites
- Python 3.10+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd library_hackathon
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Seed the database (optional):
```bash
python manage.py seed_data --create-users
```

6. Start the development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`.

## Usage Examples

### Checkout an Item
```bash
curl -X POST http://localhost:8000/api/checkout/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "item_id": 1}'
```

### Return an Item
```bash
curl -X POST http://localhost:8000/api/return/ \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": 1}'
```

### Search Items
```bash
curl "http://localhost:8000/api/items/search/?q=python"
```

### Check User Fines
```bash
curl "http://localhost:8000/api/fines/?user_id=1"
```

## Business Rules

- Users with outstanding fines exceeding $50 are blocked from checkout
- Physical items become unavailable when checked out
- Digital items support concurrent access (configurable limit)
- Fines accrue at $1 per day overdue (configurable)

## Configuration

Environment variables for production deployment:

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Secret key for cryptographic signing | Development key |
| `DJANGO_DEBUG` | Enable debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |

## Testing

```bash
python manage.py test
```

## License

This project is provided for educational purposes.
