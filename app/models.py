from flask_sqlalchemy import SQLAlchemy
from . import db
from typing import Optional, Dict, Any

class ShortenedLink(db.Model):
    __tablename__ = 'shortened_links'

    id: int = db.Column(db.Integer, primary_key=True)
    original_link: str = db.Column(db.Text, nullable=False)
    short_link: str = db.Column(db.Text, unique=True, nullable=False)
    number_of_redirections: int = db.Column(db.Integer, default=0)

    def __repr__(self) -> str:
        return f'<ShortenedLink {self.original_link} -> {self.short_link}>'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'original_link': self.original_link,
            'short_link': self.short_link,
            'number_of_redirections': self.number_of_redirections
        }
