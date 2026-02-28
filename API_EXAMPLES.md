# API Testing Examples

Quick reference for testing the Library Management System API endpoints.

## Setup

```bash
# Start server
python manage.py runserver

# In another terminal, run these commands
```

## 1. Catalog Endpoints

### List All Books

```bash
curl http://localhost:8000/api/catalog/books/ | python3 -m json.tool
```

### Get Specific Book

```bash
curl http://localhost:8000/api/catalog/books/1/ | python3 -m json.tool
```

### Search Books

```bash
curl "http://localhost:8000/api/catalog/books/?search=Clean" | python3 -m json.tool
```

### Filter Available Books

```bash
curl "http://localhost:8000/api/catalog/books/?is_available=true" | python3 -m json.tool
```

### List All Items (Polymorphic)

```bash
curl http://localhost:8000/api/catalog/items/ | python3 -m json.tool
```

## 2. User Registration & Authentication

### Register New User

```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }' | python3 -m json.tool
```

### Get Current User Profile (requires auth)

```bash
curl http://localhost:8000/api/users/me/ \
  --user admin:admin123 | python3 -m json.tool
```

## 3. Loan Operations

### Checkout a Book

```bash
curl -X POST http://localhost:8000/api/loans/checkout/ \
  -H "Content-Type: application/json" \
  --user alice:password123 \
  -d '{"item_id": 1}' | python3 -m json.tool
```

### List User's Loans

```bash
curl http://localhost:8000/api/loans/ \
  --user alice:password123 | python3 -m json.tool
```

### Return a Book

```bash
curl -X POST http://localhost:8000/api/loans/1/return/ \
  -H "Content-Type: application/json" \
  --user alice:password123 \
  -d '{"confirm": true}' | python3 -m json.tool
```

### Check User Fines

```bash
curl http://localhost:8000/api/loans/fines/ \
  --user alice:password123 | python3 -m json.tool
```

## 4. Admin Operations (Librarian Only)

### Create a New Book

```bash
curl -X POST http://localhost:8000/api/catalog/books/ \
  -H "Content-Type: application/json" \
  --user admin:admin123 \
  -d '{
    "title": "Refactoring",
    "author": "Martin Fowler",
    "isbn": "9780134757599",
    "publication_year": 2018,
    "publisher": "Addison-Wesley"
  }' | python3 -m json.tool
```

### Update a Book

```bash
curl -X PATCH http://localhost:8000/api/catalog/books/1/ \
  -H "Content-Type: application/json" \
  --user admin:admin123 \
  -d '{
    "condition": "GOOD"
  }' | python3 -m json.tool
```

### Delete a Book

```bash
curl -X DELETE http://localhost:8000/api/catalog/books/1/ \
  --user admin:admin123
```

### Create DVD

```bash
curl -X POST http://localhost:8000/api/catalog/dvds/ \
  -H "Content-Type: application/json" \
  --user admin:admin123 \
  -d '{
    "title": "The Matrix",
    "director": "The Wachowskis",
    "runtime_minutes": 136,
    "release_year": 1999
  }' | python3 -m json.tool
```

### Create eBook

```bash
curl -X POST http://localhost:8000/api/catalog/ebooks/ \
  -H "Content-Type: application/json" \
  --user admin:admin123 \
  -d '{
    "title": "Django for Beginners",
    "author": "William Vincent",
    "publication_year": 2022,
    "file_size_mb": 3.5,
    "total_licenses": 5,
    "file_format": "PDF"
  }' | python3 -m json.tool
```

## 5. Advanced Queries

### Filter Books by Author

```bash
curl "http://localhost:8000/api/catalog/books/?author=Martin" | python3 -m json.tool
```

### Filter Books by Year

```bash
curl "http://localhost:8000/api/catalog/books/?publication_year=2008" | python3 -m json.tool
```

### Order Books by Title (Descending)

```bash
curl "http://localhost:8000/api/catalog/books/?ordering=-title" | python3 -m json.tool
```

### Combined Filters

```bash
curl "http://localhost:8000/api/catalog/books/?is_available=true&ordering=title" | python3 -m json.tool
```

### Pagination

```bash
curl "http://localhost:8000/api/catalog/books/?page=1&page_size=5" | python3 -m json.tool
```

## 6. Using Python Requests

```python
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000/api"

# List books
response = requests.get(f"{BASE_URL}/catalog/books/")
print(response.json())

# Register user
data = {
    "username": "newuser",
    "email": "new@example.com",
    "password": "secure123",
    "password_confirm": "secure123"
}
response = requests.post(f"{BASE_URL}/users/register/", json=data)
print(response.json())

# Checkout book (with auth)
auth = HTTPBasicAuth('alice', 'password123')
data = {"item_id": 1}
response = requests.post(f"{BASE_URL}/loans/checkout/", json=data, auth=auth)
print(response.json())

# Get user fines
response = requests.get(f"{BASE_URL}/loans/fines/", auth=auth)
print(response.json())
```

## 7. Testing Scenarios

### Scenario 1: New Member Borrows a Book

```bash
# 1. Register
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@test.com", "password": "pass123", "password_confirm": "pass123"}'

# 2. List available books
curl http://localhost:8000/api/catalog/books/?is_available=true

# 3. Checkout book #1
curl -X POST http://localhost:8000/api/loans/checkout/ \
  --user john:pass123 \
  -H "Content-Type: application/json" \
  -d '{"item_id": 1}'

# 4. Check my loans
curl http://localhost:8000/api/loans/ --user john:pass123
```

### Scenario 2: Librarian Adds New Items

```bash
# 1. Add book
curl -X POST http://localhost:8000/api/catalog/books/ \
  --user admin:admin123 \
  -H "Content-Type: application/json" \
  -d '{"title": "New Book", "author": "Author Name", "publication_year": 2024, "isbn": "1234567890123"}'

# 2. Add DVD
curl -X POST http://localhost:8000/api/catalog/dvds/ \
  --user admin:admin123 \
  -H "Content-Type: application/json" \
  -d '{"title": "New Movie", "director": "Director Name", "runtime_minutes": 120, "release_year": 2024}'

# 3. View all items
curl http://localhost:8000/api/catalog/items/ --user admin:admin123
```

### Scenario 3: Overdue Fines

```bash
# 1. Borrow a book
curl -X POST http://localhost:8000/api/loans/checkout/ \
  --user alice:password123 \
  -H "Content-Type: application/json" \
  -d '{"item_id": 2}'

# 2. Check fines (will be $0 if not overdue)
curl http://localhost:8000/api/loans/fines/ --user alice:password123

# 3. Return the book
curl -X POST http://localhost:8000/api/loans/1/return/ \
  --user alice:password123 \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```

## Notes

- Replace `admin:admin123` with your actual admin credentials
- Replace `alice:password123` with created user credentials
- All responses return JSON
- Use `| python3 -m json.tool` for pretty-printed JSON
- Authentication uses HTTP Basic Auth (good for testing, use JWT in production)

## Status Codes

- `200 OK` - Successful GET/PUT/PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found

---

**Pro Tip**: Use tools like Postman or Insomnia for a GUI-based API testing experience!
