"""
core/logic/base.py - The OOP Foundation

This module defines the abstract base classes and interfaces that form
the foundation of the library management system's object-oriented design.

Key Components:
- AbstractBaseItem: Abstract base class for all library items
- Borrowable: Interface/Protocol for items that can be borrowed physically
- DigitalAccessible: Interface for items that can be accessed digitally
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class Borrowable(Protocol):
    """
    Interface for items that can be physically borrowed.
    
    Items implementing this interface must provide methods for
    checking out, returning, and tracking availability.
    """
    
    def check_out(self, user_id: int, due_date: Optional[datetime] = None) -> dict:
        """
        Process checkout of the item.
        
        Args:
            user_id: The ID of the user borrowing the item
            due_date: Optional custom due date, defaults to item's loan period
            
        Returns:
            dict with checkout details including due_date and transaction_id
        """
        ...
    
    def return_item(self, return_date: Optional[datetime] = None) -> dict:
        """
        Process return of the item.
        
        Args:
            return_date: Optional return date, defaults to current datetime
            
        Returns:
            dict with return details including any fines incurred
        """
        ...
    
    def is_available(self) -> bool:
        """Check if the item is available for checkout."""
        ...


@runtime_checkable
class DigitalAccessible(Protocol):
    """
    Interface for items that can be accessed digitally.
    
    Digital items don't have physical availability constraints
    but may have concurrent access limits.
    """
    
    def get_access_link(self, user_id: int) -> str:
        """
        Generate an access link for digital content.
        
        Args:
            user_id: The ID of the user requesting access
            
        Returns:
            URL string for accessing the digital content
        """
        ...
    
    def get_concurrent_access_limit(self) -> int:
        """Return the maximum number of concurrent users allowed."""
        ...


class AbstractBaseItem(ABC):
    """
    Abstract base class for all library items.
    
    This class defines the common interface and shared functionality
    for all types of library items (books, DVDs, e-books, etc.).
    
    Attributes:
        item_id: Unique identifier for the item
        title: Title of the item
        author: Author/Creator of the item
        year_published: Year the item was published/released
        genre: Genre/Category of the item
    """
    
    def __init__(
        self,
        item_id: int,
        title: str,
        author: str,
        year_published: int,
        genre: str
    ):
        self._item_id = item_id
        self._title = title
        self._author = author
        self._year_published = year_published
        self._genre = genre
    
    @property
    def item_id(self) -> int:
        return self._item_id
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def author(self) -> str:
        return self._author
    
    @property
    def year_published(self) -> int:
        return self._year_published
    
    @property
    def genre(self) -> str:
        return self._genre
    
    @abstractmethod
    def is_digital(self) -> bool:
        """
        Determine if the item is digital or physical.
        
        Returns:
            True if the item is digital, False if physical
        """
        pass
    
    @abstractmethod
    def get_loan_period_days(self) -> int:
        """
        Get the standard loan period for this item type.
        
        Returns:
            Number of days the item can be borrowed
        """
        pass
    
    @abstractmethod
    def get_item_type(self) -> str:
        """
        Get a string representation of the item type.
        
        Returns:
            String describing the item type (e.g., 'Book', 'DVD', 'EBook')
        """
        pass
    
    def calculate_due_date(self, checkout_date: Optional[datetime] = None) -> datetime:
        """
        Calculate the due date based on the item's loan period.
        
        Args:
            checkout_date: The date of checkout, defaults to now
            
        Returns:
            datetime representing when the item is due
        """
        if checkout_date is None:
            checkout_date = datetime.now()
        return checkout_date + timedelta(days=self.get_loan_period_days())
    
    def to_dict(self) -> dict:
        """
        Convert the item to a dictionary representation.
        
        Returns:
            Dictionary containing all item attributes
        """
        return {
            'item_id': self._item_id,
            'title': self._title,
            'author': self._author,
            'year_published': self._year_published,
            'genre': self._genre,
            'is_digital': self.is_digital(),
            'item_type': self.get_item_type(),
            'loan_period_days': self.get_loan_period_days(),
        }
    
    def __repr__(self) -> str:
        return f"{self.get_item_type()}(id={self._item_id}, title='{self._title}')"
    
    def __str__(self) -> str:
        return f"{self._title} by {self._author} ({self._year_published})"


class PhysicalItem(AbstractBaseItem, ABC):
    """
    Abstract base class for physical library items.
    
    Physical items can be borrowed and have availability tracking.
    They implement the Borrowable interface.
    
    Attributes:
        location: Physical location in the library (shelf/section)
        is_checked_out: Current checkout status
        current_borrower_id: ID of current borrower, if checked out
    """
    
    def __init__(
        self,
        item_id: int,
        title: str,
        author: str,
        year_published: int,
        genre: str,
        location: str = "General Section"
    ):
        super().__init__(item_id, title, author, year_published, genre)
        self._location = location
        self._is_checked_out = False
        self._current_borrower_id: Optional[int] = None
        self._checkout_date: Optional[datetime] = None
        self._due_date: Optional[datetime] = None
    
    @property
    def location(self) -> str:
        return self._location
    
    def is_digital(self) -> bool:
        """Physical items are not digital."""
        return False
    
    def is_available(self) -> bool:
        """Check if the item is available for checkout."""
        return not self._is_checked_out
    
    def check_out(self, user_id: int, due_date: Optional[datetime] = None) -> dict:
        """
        Process checkout of the physical item.
        
        Args:
            user_id: The ID of the user borrowing the item
            due_date: Optional custom due date
            
        Returns:
            dict with checkout details
            
        Raises:
            ValueError: If item is already checked out
        """
        if self._is_checked_out:
            raise ValueError(f"Item '{self._title}' is already checked out")
        
        self._is_checked_out = True
        self._current_borrower_id = user_id
        self._checkout_date = datetime.now()
        self._due_date = due_date or self.calculate_due_date(self._checkout_date)
        
        return {
            'success': True,
            'item_id': self._item_id,
            'user_id': user_id,
            'checkout_date': self._checkout_date.isoformat(),
            'due_date': self._due_date.isoformat(),
            'message': f"Successfully checked out '{self._title}'"
        }
    
    def return_item(self, return_date: Optional[datetime] = None) -> dict:
        """
        Process return of the physical item.
        
        Args:
            return_date: Optional return date, defaults to now
            
        Returns:
            dict with return details including any fines
            
        Raises:
            ValueError: If item is not checked out
        """
        if not self._is_checked_out:
            raise ValueError(f"Item '{self._title}' is not checked out")
        
        if return_date is None:
            return_date = datetime.now()
        
        result = {
            'success': True,
            'item_id': self._item_id,
            'user_id': self._current_borrower_id,
            'return_date': return_date.isoformat(),
            'due_date': self._due_date.isoformat() if self._due_date else None,
            'message': f"Successfully returned '{self._title}'"
        }
        
        # Reset checkout state
        self._is_checked_out = False
        self._current_borrower_id = None
        self._checkout_date = None
        self._due_date = None
        
        return result
    
    def to_dict(self) -> dict:
        """Extended dictionary representation including physical item details."""
        base_dict = super().to_dict()
        base_dict.update({
            'location': self._location,
            'is_available': self.is_available(),
            'current_borrower_id': self._current_borrower_id,
            'due_date': self._due_date.isoformat() if self._due_date else None,
        })
        return base_dict


class DigitalItem(AbstractBaseItem, ABC):
    """
    Abstract base class for digital library items.
    
    Digital items can be accessed online without physical constraints.
    They implement the DigitalAccessible interface.
    
    Attributes:
        file_format: Format of the digital file (PDF, EPUB, MP4, etc.)
        file_size_mb: Size of the file in megabytes
        download_url: URL for accessing the content
        concurrent_access_limit: Max concurrent users allowed
    """
    
    def __init__(
        self,
        item_id: int,
        title: str,
        author: str,
        year_published: int,
        genre: str,
        file_format: str = "PDF",
        file_size_mb: float = 0.0,
        concurrent_access_limit: int = 5
    ):
        super().__init__(item_id, title, author, year_published, genre)
        self._file_format = file_format
        self._file_size_mb = file_size_mb
        self._concurrent_access_limit = concurrent_access_limit
        self._current_access_count = 0
    
    @property
    def file_format(self) -> str:
        return self._file_format
    
    @property
    def file_size_mb(self) -> float:
        return self._file_size_mb
    
    def is_digital(self) -> bool:
        """Digital items are digital."""
        return True
    
    def get_loan_period_days(self) -> int:
        """Digital items typically have longer or unlimited access."""
        return 21  # 3 weeks default access
    
    def get_access_link(self, user_id: int) -> str:
        """
        Generate an access link for the digital content.
        
        Args:
            user_id: The ID of the user requesting access
            
        Returns:
            URL string for accessing the content
        """
        return f"/api/digital/{self._item_id}/access?user={user_id}"
    
    def get_concurrent_access_limit(self) -> int:
        """Return the maximum number of concurrent users allowed."""
        return self._concurrent_access_limit
    
    def to_dict(self) -> dict:
        """Extended dictionary representation including digital item details."""
        base_dict = super().to_dict()
        base_dict.update({
            'file_format': self._file_format,
            'file_size_mb': self._file_size_mb,
            'concurrent_access_limit': self._concurrent_access_limit,
            'current_access_count': self._current_access_count,
        })
        return base_dict
