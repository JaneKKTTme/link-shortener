from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import psycopg2

db = SQLAlchemy()

class ShortenedLink(db.Model):
    __tablename__ = 'shortened_links'

    id = db.Column(db.Integer, primary_key=True)
    long_link = db.Column(db.Text, nullable=False)
    short_link = db.Column(db.Text, unique=True, nullable=False)

    def __repr__(self):
        return f'<ShortenedLink {self.long_link} -> {self.short_link}'


def init_db():
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        try:
            with app.context():
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS shortened_links (
                    id SERIAL PRIMARY KEY,
                    long_link TEXT NOT NULL,
                    short_link TEXT NOT NULL
                );
                """
                db.session.execute(db.text(create_table_sql))
                db.session.commit()
        except Exception as e:
            print(e)
