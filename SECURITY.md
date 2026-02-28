# Security Policy

## 🔒 Security Notice

This is an **educational project** designed to demonstrate Django REST Framework concepts and best practices. While it follows security best practices, it should be reviewed and hardened before production deployment.

## ⚠️ Important Security Considerations for Production

### 1. Secret Key

The default `SECRET_KEY` in `settings.py` is insecure by design (marked as "django-insecure").

**Before deploying to production:**

- Generate a new secret key
- Store it securely in environment variables
- Never commit it to version control

```bash
# Generate a secure key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 2. Debug Mode

- Set `DEBUG = False` in production
- Configure proper error logging
- Use custom error pages (404, 500)

### 3. Database

- Do NOT use SQLite in production
- Use PostgreSQL or MySQL
- Use strong database passwords
- Restrict database access

### 4. Authentication

- The current implementation uses Basic Authentication for simplicity
- For production, implement:
  - JWT tokens (e.g., `djangorestframework-simplejwt`)
  - OAuth2 for third-party authentication
  - Session timeout
  - Password complexity requirements
  - Rate limiting on auth endpoints

### 5. HTTPS

- **Always** use HTTPS in production
- Set `SECURE_SSL_REDIRECT = True`
- Set `SESSION_COOKIE_SECURE = True`
- Set `CSRF_COOKIE_SECURE = True`

### 6. Allowed Hosts

- Configure `ALLOWED_HOSTS` with your actual domain
- Do not use wildcard (`*`)

### 7. CORS

- If building a frontend, configure CORS properly
- Don't use `CORS_ALLOW_ALL_ORIGINS = True` in production
- Whitelist specific origins only

### 8. File Uploads

- If adding file upload functionality:
  - Validate file types
  - Scan for malware
  - Limit file sizes
  - Store files outside web root

### 9. Dependencies

- Regularly update dependencies
- Monitor security advisories
- Use `pip-audit` or similar tools

## 🐛 Reporting a Vulnerability

If you discover a security vulnerability in this project:

1. **Do NOT** open a public issue
2. Email the maintainer privately (if this were a real production project)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

For this educational project, you can open an issue labeled "security" if you find security concerns.

## ✅ Security Features Implemented

This project already includes:

- ✅ Django's built-in password hashing
- ✅ CSRF protection enabled
- ✅ SQL injection protection (via Django ORM)
- ✅ XSS protection (via Django templates)
- ✅ Role-based access control
- ✅ Permission checks on sensitive endpoints
- ✅ Input validation via DRF serializers
- ✅ Environment variable support via python-decouple

## 📋 Production Deployment Checklist

Before deploying to production:

- [ ] Generate and set secure `SECRET_KEY`
- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL or MySQL
- [ ] Configure HTTPS/SSL
- [ ] Set secure cookie flags
- [ ] Implement rate limiting
- [ ] Add JWT or token authentication
- [ ] Configure logging and monitoring
- [ ] Set up backup strategy
- [ ] Implement CORS properly
- [ ] Run security audit
- [ ] Update all dependencies
- [ ] Configure firewall rules
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Implement API rate limiting
- [ ] Add cache headers
- [ ] Configure static files serving
- [ ] Set up regular backups
- [ ] Document deployment process

## 📚 Security Resources

- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django REST Framework Security](https://www.django-rest-framework.org/topics/security/)
- [12 Factor App](https://12factor.net/)

## 🔄 Regular Security Maintenance

For production systems:

1. Update Django and dependencies monthly
2. Review security advisories weekly
3. Monitor logs for suspicious activity
4. Rotate secrets periodically
5. Conduct security audits quarterly
6. Test backup/restore procedures
7. Keep documentation updated

---

**Remember**: Security is an ongoing process, not a one-time setup.
