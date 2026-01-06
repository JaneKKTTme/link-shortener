from flask_sqlalchemy import SQLAlchemy
from . import db

class ShortenedLink(db.Model):
    __tablename__ = 'shortened_links'

    id = db.Column(db.Integer, primary_key=True)
    original_link = db.Column(db.Text, nullable=False)
    short_link = db.Column(db.Text, unique=True, nullable=False)

    def __repr__(self):
        return f'<ShortenedLink {self.original_link} -> {self.short_link}>'
