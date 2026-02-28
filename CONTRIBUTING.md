# Contributing to Library Management System

Thank you for your interest in contributing to the Library Management System! This document provides guidelines for contributing to this project.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment (OS, Python version, Django version)
- Any relevant error messages or logs

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:

- A clear description of the enhancement
- Why this enhancement would be useful
- Examples of how it would work

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Write clear commit messages** that describe your changes
3. **Add tests** for any new functionality
4. **Ensure all tests pass**: Run `python manage.py test`
5. **Update documentation** if needed
6. **Follow the existing code style**

## 📋 Development Setup

```bash
# Clone your fork
git clone https://github.com/FredickMbithi/library-management-system.git
cd library-management-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Run tests
python manage.py test
```

## 🎯 Coding Standards

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to classes and functions
- Keep functions focused and small

### Django Best Practices

- Use Django's built-in features when possible
- Keep business logic in services, not views
- Write model methods for domain behavior
- Use Django's form validation

### Testing

- Write tests for new features
- Maintain or improve test coverage
- Test edge cases and error conditions
- Use descriptive test names

### Documentation

- Update README for significant changes
- Add docstrings to new classes/functions
- Update API documentation if endpoints change
- Include examples where helpful

## 🔀 Git Workflow

1. **Create a feature branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and commit**:

   ```bash
   git add .
   git commit -m "Add feature: description of changes"
   ```

3. **Keep your branch updated**:

   ```bash
   git fetch origin
   git rebase origin/main
   ```

4. **Push your changes**:

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** on GitHub

## ✅ Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass (`python manage.py test`)
- [ ] New tests added for new functionality
- [ ] Documentation updated if needed
- [ ] Commit messages are clear and descriptive
- [ ] No merge conflicts with main branch
- [ ] No sensitive data (passwords, keys) in code

## 🎨 Areas for Contribution

We welcome contributions in these areas:

### Features

- Reservation system for checked-out items
- Email notifications for due dates
- Payment processing for fines
- Book recommendation system
- Multi-branch library support
- Analytics dashboard
- Export functionality (CSV, PDF)

### Technical Improvements

- JWT authentication
- API rate limiting
- Caching implementation
- Performance optimizations
- Docker support
- CI/CD pipeline
- API versioning

### Documentation

- More API examples
- Video tutorials
- Architecture diagrams
- Deployment guides
- Internationalization (i18n)

### Testing

- Increase test coverage
- Add integration tests
- Performance testing
- Load testing
- Security testing

## 📚 Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Git Best Practices](https://git-scm.com/book/en/v2)

## 🐛 Issue Labels

We use these labels to organize issues:

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `question` - Further information requested

## 💬 Questions?

If you have questions about contributing, feel free to:

- Create a discussion in GitHub Discussions
- Open an issue with the `question` label
- Check existing issues and pull requests

## 📜 Code of Conduct

Be respectful and inclusive. We're all here to learn and build together.

---

**Thank you for contributing to Library Management System!** 🎉
