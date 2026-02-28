# 🚀 Getting Started - Library Management System

This guide will help you set up and run the Library Management System in just a few minutes.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for version control)

## Quick Start

### 1. Set Up Virtual Environment

```bash
# Navigate to project directory
cd library-management-system

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Expected output: Installation of Django, DRF, django-filter, etc.

### 3. Configure Environment (Optional)

```bash
# Copy example environment file
cp .env.example .env

# Edit if needed (defaults work fine for development)
# nano .env
```

### 4. Set Up Database

```bash
# Create database tables
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: (your choice, e.g., admin123)
```

### 5. Run the Server

```bash
python manage.py runserver
```

Server will start at: **http://localhost:8000**

## 🎯 Access Points

### Admin Interface

- URL: http://localhost:8000/admin/
- Login with your superuser credentials
- Manage books, DVDs, eBooks, users, and loans

### API Root

- URL: http://localhost:8000/api/
- Browse available endpoints

### API Documentation

**Catalog:**

- Books: http://localhost:8000/api/catalog/books/
- DVDs: http://localhost:8000/api/catalog/dvds/
- eBooks: http://localhost:8000/api/catalog/ebooks/
- All Items: http://localhost:8000/api/catalog/items/

**Loans:**

- My Loans: http://localhost:8000/api/loans/
- Checkout: POST to http://localhost:8000/api/loans/checkout/
- Return: POST to http://localhost:8000/api/loans/{id}/return/

**Users:**

- Register: POST to http://localhost:8000/api/users/register/
- My Profile: http://localhost:8000/api/users/me/

## 🧪 Testing the System

### Run Tests

```bash
# Run all tests (50+ tests)
python manage.py test

# Run with verbose output
python manage.py test --verbosity=2

# Run specific app tests
python manage.py test apps.accounts
python manage.py test apps.catalog
python manage.py test apps.loans
```

### Create Sample Data

Use the admin interface or Django shell:

```bash
python manage.py shell
```

Then:

```python
from apps.catalog.models import Book, DVD, EBook
from django.contrib.auth import get_user_model

User = get_user_model()

# Create a book
Book.objects.create(
    title="Clean Code",
    author="Robert C. Martin",
    isbn="9780132350884",
    publication_year=2008
)

# Create a DVD
DVD.objects.create(
    title="Inception",
    director="Christopher Nolan",
    runtime_minutes=148,
    release_year=2010
)

# Create an eBook
EBook.objects.create(
    title="Python Crash Course",
    author="Eric Matthes",
    publication_year=2019,
    file_size_mb=5.2,
    total_licenses=3
)

# Create a member user
member = User.objects.create_user(
    username='alice',
    email='alice@example.com',
    password='password123',
    role='MEMBER'
)

print("Sample data created!")
```

## 📋 Quick API Testing with curl

### 1. List All Books

```bash
curl http://localhost:8000/api/catalog/books/
```

### 2. Register a New User

```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "secure123",
    "password_confirm": "secure123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 3. Checkout a Book

```bash
curl -X POST http://localhost:8000/api/loans/checkout/ \
  -H "Content-Type: application/json" \
  --user alice:password123 \
  -d '{"item_id": 1}'
```

## 🔑 Default Credentials

After running `createsuperuser`:

**Admin/Librarian:**

- Username: admin
- Password: (what you set)
- Role: LIBRARIAN (auto-assigned to superusers)

**Sample Member (if created):**

- Username: alice
- Password: password123
- Role: MEMBER

## 🐛 Troubleshooting

### "No module named 'decouple'"

```bash
# Ensure venv is activated
source venv/bin/activate
pip install -r requirements.txt
```

### "django.db.utils.OperationalError"

```bash
# Delete db and recreate
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### "Port already in use"

```bash
# Use different port
python manage.py runserver 8001
```

### Tests Failing

```bash
# Ensure you're in venv and dependencies are installed
source venv/bin/activate
pip install -r requirements.txt
python manage.py test
```

## 📚 Next Steps

1. **Explore the Admin Panel**: Add books, DVDs, eBooks
2. **Create Test Users**: Create members via admin or registration endpoint
3. **Test Borrowing**: Checkout items as a member
4. **Check Fines**: Try returning items late and view fine calculations
5. **Read API Docs**: Check `Readme.md` for complete API reference

## 🎓 Learning Resources

- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **Project README**: See `Readme.md` for architecture details

## 💡 Tips

- Use the browsable API by visiting endpoints in your browser
- The admin panel is perfect for quick data management
- All tests are in `apps/*/tests.py` - great learning resource!
- Check `apps/loans/services.py` for business logic examples

---

**Ready to build? Start coding!** 🚀
