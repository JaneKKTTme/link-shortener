from flask_sqlalchemy import SQLAlchemy
import psycopg2

db = SQLAlchemy()

class ShortenedLink(db.Model):
    __tablename__ = 'shortened_links'

    id = db.Column(db.Integer, primary_key=True)
    original_link = db.Column(db.Text, nullable=False)
    short_link = db.Column(db.Text, unique=True, nullable=False)

    def __repr__(self):
        return f'<ShortenedLink {self.original_link} -> {self.short_link}'


def init_db(app):
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        try:
            with app.app_context():
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS shortened_links (
                    id SERIAL PRIMARY KEY,
                    original_link TEXT NOT NULL,
                    short_link TEXT NOT NULL
                );
                """
                db.session.execute(db.text(create_table_sql))
                db.session.commit()
        except Exception as e:
            print(e)


def reset_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
