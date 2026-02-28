"""
core/logic/items.py - Polymorphism Implementation

This module contains the concrete implementations of library items.
Each subclass implements the abstract methods and may override behavior
to demonstrate polymorphism.

Item Types:
- Book: Standard physical book with 14-day loan period
- DVD: Physical DVD with 7-day loan period (shorter due to popularity)
- Magazine: Physical periodical with 7-day loan period
- EBook: Digital book with unlimited access period
- AudioBook: Digital audio content
"""

from datetime import datetime, timedelta
from typing import Optional

from .base import PhysicalItem, DigitalItem


class Book(PhysicalItem):
    """
    Represents a physical book in the library.
    
    Books have a standard 14-day loan period and can include
    additional metadata like ISBN and page count.
    
    Attributes:
        isbn: International Standard Book Number
        pages: Number of pages in the book
        edition: Edition number/description
    """
    
    LOAN_PERIOD_DAYS = 14
    
    def __init__(
        self,
        item_id: int,
        title: str,
        author: str,
        year_published: int,
        genre: str,
        location: str = "General Section",
        isbn: str = "",
        pages: int = 0,
        edition: str = "1st"
    ):
        super().__init__(item_id, title, author, year_published, genre, location)
        self._isbn = isbn
        self._pages = pages
        self._edition = edition
    
    @property
    def isbn(self) -> str:
        return self._isbn
    
    @property
    def pages(self) -> int:
        return self._pages
    
    @property
    def edition(self) -> str:
        return self._edition
    
    def get_loan_period_days(self) -> int:
        """Books have a 14-day loan period."""
        return self.LOAN_PERIOD_DAYS
    
    def get_item_type(self) -> str:
        return "Book"
    
    def check_out(self, user_id: int, due_date: Optional[datetime] = None) -> dict:
        """
        Process checkout with book-specific messaging.
        
        Overrides parent to add book-specific details to response.
        """
        result = super().check_out(user_id, due_date)
        result['item_type'] = 'Book'
        result['isbn'] = self._isbn
        return result
    
    def to_dict(self) -> dict:
        """Extended dictionary with book-specific attributes."""
        base_dict = super().to_dict()
        base_dict.update({
            'isbn': self._isbn,
            'pages': self._pages,
            'edition': self._edition,
        })
        return base_dict


class DVD(PhysicalItem):
    """
    Represents a physical DVD in the library.
    
    DVDs have a shorter 7-day loan period due to high demand
    and include runtime and rating information.
    
    Attributes:
        runtime_minutes: Length of the DVD content in minutes
        rating: Content rating (G, PG, PG-13, R, etc.)
        director: Director of the film/content
    """
    
    LOAN_PERIOD_DAYS = 7
    
    def __init__(
        self,
        item_id: int,
        title: str,
        author: str,  # For DVDs, this is typically the director
        year_published: int,
        genre: str,
        location: str = "Media Section",
        runtime_minutes: int = 0,
        rating: str = "NR",
        director: str = ""
    ):
        super().__init__(item_id, title, author, year_published, genre, location)
        self._runtime_minutes = runtime_minutes
        self._rating = rating
        self._director = director or author
    
    @property
    def runtime_minutes(self) -> int:
        return self._runtime_minutes
    
    @property
    def rating(self) -> str:
        return self._rating
    
    @property
    def director(self) -> str:
        return self._director
    
    def get_loan_period_days(self) -> int:
        """DVDs have a shorter 7-day loan period."""
        return self.LOAN_PERIOD_DAYS
    
    def get_item_type(self) -> str:
        return "DVD"
    
    def check_out(self, user_id: int, due_date: Optional[datetime] = None) -> dict:
        """
        Process checkout with DVD-specific handling.
        
        DVDs might have additional restrictions or notifications.
        """
        result = super().check_out(user_id, due_date)
        result['item_type'] = 'DVD'
        result['runtime_minutes'] = self._runtime_minutes
        result['note'] = "Return DVD in original case"
        return result
    
    def to_dict(self) -> dict:
        """Extended dictionary with DVD-specific attributes."""
        base_dict = super().to_dict()
        base_dict.update({
            'runtime_minutes': self._runtime_minutes,
            'rating': self._rating,
            'director': self._director,
        })
        return base_dict


class Magazine(PhysicalItem):
    """
    Represents a physical magazine/periodical in the library.
    
    Magazines have a 7-day loan period and include issue information.
    
    Attributes:
        issue_number: The issue number of the magazine
        issue_date: Publication date of this specific issue
        publisher: Publisher of the magazine
    """
    
    LOAN_PERIOD_DAYS = 7
    
    def __init__(
        self,
        item_id: int,
        title: str,
        author: str,
        year_published: int,
        genre: str,
        location: str = "Periodicals Section",
        issue_number: str = "",
        issue_date: str = "",
        publisher: str = ""
    ):
        super().__init__(item_id, title, author, year_published, genre, location)
        self._issue_number = issue_number
        self._issue_date = issue_date
        self._publisher = publisher
    
    @property
    def issue_number(self) -> str:
        return self._issue_number
    
    @property
    def issue_date(self) -> str:
        return self._issue_date
    
    @property
    def publisher(self) -> str:
        return self._publisher
    
    def get_loan_period_days(self) -> int:
        """Magazines have a 7-day loan period."""
        return self.LOAN_PERIOD_DAYS
    
    def get_item_type(self) -> str:
        return "Magazine"
    
    def to_dict(self) -> dict:
        """Extended dictionary with magazine-specific attributes."""
        base_dict = super().to_dict()
        base_dict.update({
            'issue_number': self._issue_number,
            'issue_date': self._issue_date,
            'publisher': self._publisher,
        })
        return base_dict


class EBook(DigitalItem):
    """
    Represents a digital e-book in the library.
    
    E-books can be accessed by multiple users simultaneously
    (up to the concurrent access limit) and don't require physical returns.
    
    Attributes:
        isbn: International Standard Book Number (digital edition)
        pages: Number of pages equivalent
        drm_protected: Whether the e-book has DRM protection
    """
    
    LOAN_PERIOD_DAYS = 21
    
    def __init__(
        self,
        item_id: int,
        title: str,
        author: str,
        year_published: int,
        genre: str,
        file_format: str = "EPUB",
        file_size_mb: float = 0.0,
        concurrent_access_limit: int = 5,
        isbn: str = "",
        pages: int = 0,
        drm_protected: bool = True
    ):
        super().__init__(
            item_id, title, author, year_published, genre,
            file_format, file_size_mb, concurrent_access_limit
        )
        self._isbn = isbn
        self._pages = pages
        self._drm_protected = drm_protected
    
    @property
    def isbn(self) -> str:
        return self._isbn
    
    @property
    def pages(self) -> int:
        return self._pages
    
    @property
    def drm_protected(self) -> bool:
        return self._drm_protected
    
    def get_loan_period_days(self) -> int:
        """E-books have a 21-day access period."""
        return self.LOAN_PERIOD_DAYS
    
    def get_item_type(self) -> str:
        return "EBook"
    
    def get_access_link(self, user_id: int) -> str:
        """
        Generate a secure access link for the e-book.
        
        E-books may include DRM authorization in the link.
        """
        base_link = super().get_access_link(user_id)
        if self._drm_protected:
            return f"{base_link}&drm=true"
        return base_link
    
    def to_dict(self) -> dict:
        """Extended dictionary with e-book-specific attributes."""
        base_dict = super().to_dict()
        base_dict.update({
            'isbn': self._isbn,
            'pages': self._pages,
            'drm_protected': self._drm_protected,
        })
        return base_dict


class AudioBook(DigitalItem):
    """
    Represents a digital audiobook in the library.
    
    Audiobooks include narrator information and duration details.
    
    Attributes:
        narrator: Person who narrated the audiobook
        duration_hours: Length of the audiobook in hours
        chapters: Number of chapters/tracks
    """
    
    LOAN_PERIOD_DAYS = 14
    
    def __init__(
        self,
        item_id: int,
        title: str,
        author: str,
        year_published: int,
        genre: str,
        file_format: str = "MP3",
        file_size_mb: float = 0.0,
        concurrent_access_limit: int = 3,
        narrator: str = "",
        duration_hours: float = 0.0,
        chapters: int = 0
    ):
        super().__init__(
            item_id, title, author, year_published, genre,
            file_format, file_size_mb, concurrent_access_limit
        )
        self._narrator = narrator
        self._duration_hours = duration_hours
        self._chapters = chapters
    
    @property
    def narrator(self) -> str:
        return self._narrator
    
    @property
    def duration_hours(self) -> float:
        return self._duration_hours
    
    @property
    def chapters(self) -> int:
        return self._chapters
    
    def get_loan_period_days(self) -> int:
        """Audiobooks have a 14-day access period."""
        return self.LOAN_PERIOD_DAYS
    
    def get_item_type(self) -> str:
        return "AudioBook"
    
    def to_dict(self) -> dict:
        """Extended dictionary with audiobook-specific attributes."""
        base_dict = super().to_dict()
        base_dict.update({
            'narrator': self._narrator,
            'duration_hours': self._duration_hours,
            'chapters': self._chapters,
        })
        return base_dict


# Factory function to create items from dictionary data
def create_item_from_dict(data: dict):
    """
    Factory function to create the appropriate item type from dictionary data.
    
    Args:
        data: Dictionary containing item data with 'item_type' key
        
    Returns:
        An instance of the appropriate item subclass
        
    Raises:
        ValueError: If item_type is unknown
    """
    item_type = data.get('item_type', '').lower()
    
    # Common fields
    common_fields = {
        'item_id': data.get('item_id', data.get('id', 0)),
        'title': data.get('title', ''),
        'author': data.get('author', ''),
        'year_published': data.get('year_published', data.get('year', 0)),
        'genre': data.get('genre', ''),
    }
    
    if item_type == 'book':
        return Book(
            **common_fields,
            location=data.get('location', 'General Section'),
            isbn=data.get('isbn', ''),
            pages=data.get('pages', 0),
            edition=data.get('edition', '1st'),
        )
    
    elif item_type == 'dvd':
        return DVD(
            **common_fields,
            location=data.get('location', 'Media Section'),
            runtime_minutes=data.get('runtime_minutes', data.get('runtime', 0)),
            rating=data.get('rating', 'NR'),
            director=data.get('director', data.get('author', '')),
        )
    
    elif item_type == 'magazine':
        return Magazine(
            **common_fields,
            location=data.get('location', 'Periodicals Section'),
            issue_number=data.get('issue_number', ''),
            issue_date=data.get('issue_date', ''),
            publisher=data.get('publisher', ''),
        )
    
    elif item_type == 'ebook':
        return EBook(
            **common_fields,
            file_format=data.get('file_format', 'EPUB'),
            file_size_mb=data.get('file_size_mb', 0.0),
            concurrent_access_limit=data.get('concurrent_access_limit', 5),
            isbn=data.get('isbn', ''),
            pages=data.get('pages', 0),
            drm_protected=data.get('drm_protected', True),
        )
    
    elif item_type == 'audiobook':
        return AudioBook(
            **common_fields,
            file_format=data.get('file_format', 'MP3'),
            file_size_mb=data.get('file_size_mb', 0.0),
            concurrent_access_limit=data.get('concurrent_access_limit', 3),
            narrator=data.get('narrator', ''),
            duration_hours=data.get('duration_hours', 0.0),
            chapters=data.get('chapters', 0),
        )
    
    else:
        raise ValueError(f"Unknown item type: {item_type}")
