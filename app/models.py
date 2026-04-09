"""Database models for URL shortening service."""

from flask_sqlalchemy import SQLAlchemy
from . import db
from typing import Optional, Dict, Any

class ShortenedLink(db.Model):
    """Database model for storing shortened URL mappings.
    
    Attributes:
        id: Unique identifier for the link record.
        original_link: Original long URL that was shortened.
        short_link: Unique short code (8 characters) for the original URL.
        number_of_redirections: Counter tracking how many times the short link was accessed.
    
    Table name:
        shortened_links
        
    Example:
        >>> link = ShortenedLink(
        ...  original_link="https://example.com/very/long/url",
        ...  short_link="abc12345"
        ... )
        >>> db.session.add(link)
        >>> db.session.commit()
    """

    __tablename__ = 'shortened_links'

    id: int = db.Column(db.Integer, primary_key=True)
    """Auto-incrementing primary key."""

    original_link: str = db.Column(db.Text, nullable=False)
    """Original long URL that was shortened. Cannot be null."""

    short_link: str = db.Column(db.Text, unique=True, nullable=False)
    """Unique short code (8 characters) for the original URL. Must be unique."""

    number_of_redirections: int = db.Column(db.Integer, default=0)
    """Counter tracking how many times the short link was accessed. Defaults to 0."""   


    def __repr__(self) -> str:
        """Return string representation of the ShortenedLink instance.
        
        Returns:
            String showing the mapping from original to short link.
            
        Example:
            >>> repr(link)
            '<ShortenedLink https://example.com -> abc12345>'
        """
        return f'<ShortenedLink {self.original_link} -> {self.short_link}>'

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary for JSON serialization.
        
        Returns:
            Dictionary containing all model fields with their current values.
            
        Example:
            >>> link.to_dict()
            {
                'id': 1,
                'original_link': 'https://example.com',
                'short_link': 'abc12345',
                'number_of_redirections': 42
            }
        """
        return {
            'id': self.id,
            'original_link': self.original_link,
            'short_link': self.short_link,
            'number_of_redirections': self.number_of_redirections
        }
