# 🎯 QUICK START GUIDE

## What I've Done

✅ **Reorganized Your Workspace**

- Created proper Django project structure with `library_system/` config folder
- Organized code into three apps: `accounts`, `catalog`, and `loans`
- Added all necessary Django configuration files
- Created comprehensive README documentation

✅ **Files Created/Organized**

- Project config: `settings.py`, `urls.py`, `wsgi.py`, `manage.py`
- App configurations: `apps.py`, `admin.py` for each app
- Environment template: `.env.example`
- Git ignore rules: `.gitignore`

## 🚀 Next Steps (In Order)

### Step 1: Set Up Virtual Environment (5 minutes)

```bash
cd "/home/ghost/Advanced Library Management System"

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

### Step 2: Install Dependencies (2 minutes)

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment (2 minutes)

```bash
# Copy environment template
cp .env.example .env

# Generate a secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Edit .env and paste the generated key
nano .env  # or use: code .env
```

In `.env`, set:

```
SECRET_KEY=<paste-the-generated-key-here>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Step 4: Initialize Database (3 minutes)

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

When prompted:

- Username: `admin` (or your choice)
- Email: your email
- Password: create a secure password

### Step 5: Run the Server (1 minute)

```bash
python manage.py runserver
```

Visit:

- 🌐 API Root: http://localhost:8000/api/
- 👤 Admin Panel: http://localhost:8000/admin/

### Step 6: Load Sample Data (Optional - 5 minutes)

You can create sample data through the admin panel or Django shell:

```bash
python manage.py shell
```

Then in the shell:

```python
from apps.accounts.models import User
from apps.catalog.models import Book, DVD, EBook
from decimal import Decimal

# Create a member user
member = User.objects.create_user(
    username='alice',
    password='testpass123',
    email='alice@example.com',
    role=User.Role.MEMBER
)

# Create a librarian
librarian = User.objects.create_user(
    username='librarian',
    password='testpass123',
    email='librarian@example.com',
    role=User.Role.LIBRARIAN
)

# Create some books
Book.objects.create(
    title='Clean Code',
    author='Robert Martin',
    isbn='978-0132350884',
    publication_year=2008,
    loan_period_days=14
)

Book.objects.create(
    title='The Pragmatic Programmer',
    author='Hunt & Thomas',
    isbn='978-0201616224',
    publication_year=1999,
    loan_period_days=14
)

# Create a DVD
DVD.objects.create(
    title='The Matrix',
    director='Wachowski Brothers',
    duration_minutes=136,
    loan_period_days=7
)

# Create an E-Book
EBook.objects.create(
    title='Domain-Driven Design',
    author='Eric Evans',
    file_size_mb=Decimal('8.5'),
    download_link='https://example.com/ddd.pdf',
    total_licenses=5
)

print("Sample data created successfully!")
exit()
```

### Step 7: Test the API (5 minutes)

#### Using curl:

```bash
# List all books
curl http://localhost:8000/api/catalog/books/

# Search for a book
curl "http://localhost:8000/api/catalog/books/?search=Clean"

# Filter available items
curl "http://localhost:8000/api/catalog/items/?is_available=true"
```

#### Using the admin panel:

1. Go to http://localhost:8000/admin/
2. Login with your superuser credentials
3. Explore the Catalog, Loans, and Users sections

### Step 8: Run Tests (2 minutes)

```bash
# Run all tests
python manage.py test

# Run with verbose output
python manage.py test -v 2

# Run specific app tests
python manage.py test apps.loans
```

## 🎓 Understanding the System

### User Roles

**Members** can:

- Browse catalog (read-only)
- Borrow available items
- Return borrowed items
- View their own loans

**Librarians** can:

- Everything members can do
- Create/edit/delete catalog items
- View all loans
- Manage all users

### Loan Lifecycle

1. **Member borrows item**
   - POST to `/api/loans/borrow/` with `item_id`
   - Item marked as unavailable
   - Due date automatically calculated

2. **Item becomes overdue**
   - System automatically calculates if `due_at < now`
   - Fines accrue at $1/day
   - User blocked from borrowing if fines ≥ $10

3. **Member returns item**
   - POST to `/api/loans/<id>/return/`
   - Item marked as available
   - Loan record preserved for history

### Fine Calculation

- **Rate**: $1.00 per day overdue
- **Blocking threshold**: $10.00 total fines
- **Note**: Fines are calculated dynamically, not stored

## 📚 Common Commands Reference

```bash
# Start development server
python manage.py runserver

# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell (interactive Python)
python manage.py shell

# Run tests
python manage.py test

# Collect static files (for production)
python manage.py collectstatic

# Check for issues
python manage.py check
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'apps'"

**Solution**: Make sure you're in the project root directory:

```bash
cd "/home/ghost/Advanced Library Management System"
```

### "django.db.utils.OperationalError: no such table"

**Solution**: Run migrations:

```bash
python manage.py migrate
```

### Import errors in models

**Solution**: Ensure all `__init__.py` files exist in app directories

## 🎯 What to Work On Next

1. **Test the current functionality** - Make sure all endpoints work
2. **Add more sample data** - Populate your database for testing
3. **Customize the models** - Add fields specific to your needs
4. **Enhance the API** - Add pagination, more filters, etc.
5. **Add frontend** - Build a React/Vue frontend or use DRF's browsable API
6. **Deploy** - Set up for production with PostgreSQL and proper hosting

## 📞 Need Help?

- Check the main [README.md](Readme.md) for detailed documentation
- Django documentation: https://docs.djangoproject.com/
- DRF documentation: https://www.django-rest-framework.org/

---

**You're all set! Start with Step 1 above.** 🚀
