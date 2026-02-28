#!/bin/bash
# Library Management System - Quick Demo Script
# This script demonstrates the key features of the system

echo "🎯 Library Management System - Interactive Demo"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if server is running
if ! curl -s http://localhost:8000 > /dev/null; then
    echo "⚠️  Server not running. Starting development server..."
    echo "Please run in another terminal:"
    echo "  source venv/bin/activate"
    echo "  python manage.py runserver"
    echo ""
    read -p "Press Enter when server is ready..."
fi

echo ""
echo "${BLUE}=== 1. Catalog Endpoints ===${NC}"
echo ""

echo "${GREEN}Listing all books:${NC}"
curl -s http://localhost:8000/api/catalog/books/ | python3 -m json.tool | head -30
echo ""
read -p "Press Enter to continue..."

echo ""
echo "${GREEN}Searching for books:${NC}"
curl -s "http://localhost:8000/api/catalog/books/?search=Clean" | python3 -m json.tool | head -20
echo ""
read -p "Press Enter to continue..."

echo ""
echo "${BLUE}=== 2. User Management ===${NC}"
echo ""

echo "${GREEN}Registering new user 'demo_user':${NC}"
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "email": "demo@example.com",
    "password": "demo123pass",
    "password_confirm": "demo123pass",
    "first_name": "Demo",
    "last_name": "User"
  }' 2>/dev/null | python3 -m json.tool
echo ""
read -p "Press Enter to continue..."

echo ""
echo "${BLUE}=== 3. Loan Operations ===${NC}"
echo ""

# Check if admin exists
echo "${GREEN}Listing available books:${NC}"
curl -s "http://localhost:8000/api/catalog/books/?is_available=true" | python3 -m json.tool | head -30
echo ""

echo "${GREEN}Note: To borrow a book, you need authentication.${NC}"
echo "Try these commands manually with your credentials:"
echo ""
echo "# Borrow book #1"
echo "curl -X POST http://localhost:8000/api/loans/checkout/ \\"
echo "  --user demo_user:demo123pass \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"item_id\": 1}'"
echo ""
echo "# Check your loans"
echo "curl http://localhost:8000/api/loans/ --user demo_user:demo123pass"
echo ""
echo "# Return book"
echo "curl -X POST http://localhost:8000/api/loans/1/return/ \\"
echo "  --user demo_user:demo123pass \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"confirm\": true}'"
echo ""
read -p "Press Enter to continue..."

echo ""
echo "${BLUE}=== 4. Admin Panel ===${NC}"
echo ""
echo "Visit the admin panel at: ${GREEN}http://localhost:8000/admin/${NC}"
echo ""
echo "Login with your superuser credentials to:"
echo "  ✓ Manage books, DVDs, and eBooks"
echo "  ✓ View all users and their roles"
echo "  ✓ Monitor loans and fine status"
echo "  ✓ Perform CRUD operations"
echo ""
read -p "Press Enter to continue..."

echo ""
echo "${BLUE}=== 5. API Documentation ===${NC}"
echo ""
echo "Full API documentation available at:"
echo "  ${GREEN}http://localhost:8000/api/${NC} (Browsable API)"
echo ""
echo "Key endpoints:"
echo "  Catalog: /api/catalog/books/, /api/catalog/dvds/, /api/catalog/ebooks/"
echo "  Loans:   /api/loans/, /api/loans/checkout/, /api/loans/{id}/return/"
echo "  Users:   /api/users/, /api/users/register/, /api/users/me/"
echo ""

echo ""
echo "${BLUE}=== 6. Running Tests ===${NC}"
echo ""
echo "${GREEN}Test suite includes 50+ tests. Run with:${NC}"
echo "  python manage.py test"
echo ""
echo "Sample output:"
echo "  Found 50 test(s)."
echo "  .................................................."
echo "  Ran 50 tests in 15.080s"
echo "  OK"
echo ""
read -p "Press Enter to continue..."

echo ""
echo "${BLUE}=== Demo Complete! ===${NC}"
echo ""
echo "📚 What you've seen:"
echo "  ✓ RESTful API for library catalog"
echo "  ✓ User registration and authentication"
echo "  ✓ Loan management system"
echo "  ✓ Admin panel for management"
echo "  ✓ Comprehensive test coverage"
echo ""
echo "📖 Next steps:"
echo "  1. Explore the admin panel"
echo "  2. Try the API endpoints with curl or Postman"
echo "  3. Review the code in apps/ directory"
echo "  4. Check PROJECT_STATUS.md for details"
echo ""
echo "📄 Documentation:"
echo "  • README.md - Full project documentation"
echo "  • QUICKSTART.md - Getting started guide"
echo "  • API_EXAMPLES.md - API testing examples"
echo "  • PROJECT_STATUS.md - Project overview"
echo ""
echo "Thank you for checking out the Library Management System! 🎉"
echo ""
