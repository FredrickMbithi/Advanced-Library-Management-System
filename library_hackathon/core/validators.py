"""
core/validators.py - Input Validation and Sanitization

Provides reusable validators for input sanitization and security.
"""

import re
import html
from django.core.exceptions import ValidationError


def sanitize_string(value: str, max_length: int = 500) -> str:
    """
    Sanitize string input to prevent XSS and injection attacks.
    
    Args:
        value: The string to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not value:
        return value
    
    # Escape HTML entities
    value = html.escape(str(value).strip())
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
    
    return value


def validate_no_script_tags(value: str) -> str:
    """
    Validate that input contains no script tags or dangerous content.
    
    Raises:
        ValidationError: If dangerous content is detected
    """
    if not value:
        return value
    
    # Pattern to detect script tags and event handlers
    dangerous_patterns = [
        r'<\s*script',
        r'javascript\s*:',
        r'on\w+\s*=',
        r'<\s*iframe',
        r'<\s*object',
        r'<\s*embed',
        r'expression\s*\(',
        r'url\s*\(\s*["\']?\s*data:',
    ]
    
    value_lower = value.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, value_lower):
            raise ValidationError(
                'Input contains potentially dangerous content'
            )
    
    return value


def validate_isbn(value: str) -> str:
    """
    Validate ISBN format (ISBN-10 or ISBN-13).
    
    Args:
        value: ISBN string
        
    Returns:
        Validated ISBN
        
    Raises:
        ValidationError: If format is invalid
    """
    if not value:
        return value
    
    # Remove hyphens and spaces
    clean_isbn = re.sub(r'[-\s]', '', value)
    
    # Check format
    if len(clean_isbn) == 10:
        if not re.match(r'^\d{9}[\dXx]$', clean_isbn):
            raise ValidationError('Invalid ISBN-10 format')
    elif len(clean_isbn) == 13:
        if not re.match(r'^\d{13}$', clean_isbn):
            raise ValidationError('Invalid ISBN-13 format')
    elif clean_isbn:
        raise ValidationError('ISBN must be 10 or 13 characters')
    
    return value


def validate_positive_integer(value: int, field_name: str = 'Value') -> int:
    """
    Validate that value is a non-negative integer.
    """
    if value is not None and value < 0:
        raise ValidationError(f'{field_name} must be non-negative')
    return value


def validate_year(value: int, min_year: int = 1000) -> int:
    """
    Validate year is within acceptable range.
    """
    from django.utils import timezone
    current_year = timezone.now().year
    
    if value < min_year or value > current_year + 2:
        raise ValidationError(
            f'Year must be between {min_year} and {current_year + 2}'
        )
    return value
