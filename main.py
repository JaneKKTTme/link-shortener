from flask import Flask, render_template, request
from pyshorteners import Shortener
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from urllib.parse import urlparse
import psycopg2
import os

app = Flask(__name__)
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app, mocel_class=Base)
with app.app_context():
    db.create_all()

class Base(DeclarativeBase):
    pass

class ShortenedLink(Base):
    __tablename__ = "shortened_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    long_link: Mapped[str] = mapped_column(unique=True)
    short_link: Mapped[str]


def shorten_link(url):
    shortener = Shortener()
    return shortener.clckru.short(url)

def expand_link(shortened_url):
    shortener = Shortener()
    return shortener.clckru.expand(shortened_url)

def is_valid_url(url):
    try:
        result = urlparse(url=url)
        if not all([result.scheme, result.netloc]):
            return False
        if result.scheme not in ['https', 'http', 'ftp']:
            return False
        return True
    except Exception:
        return False


@app.route('/', methods=['GET', 'POST'])
def link_shorter_page():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if not url:
            return render_template('link_shorter_page.html', 
                                 error="Пожалуйста, введите URL")
        if not is_valid_url(url):
            return render_template('link_shorter_page.html',
                error='ERROR')
        try:
            output = shorten_link(url)
            shortened_link = ShortenedLink(
                long_link = url,
                short_link = output,
            )
            db.session.add(shortened_link)
            db.session.commit()
            output = db.session.execute(db.select(ShortenedLink).filter_by(long_link=url)).scalar_one()
            return render_template('link_shorter_page.html',
                output=output)
        except Exception as e:
            return render_template('link_shorter_page.html',
                error='ERROR:'+e)
    '''
        try:
            db.execute(
                "INSERT INTO shortened_links (long_link, short_link) VALUES (?, ?)", 
                (url, output)
            )
            db.commit()
        except db.IntegrityError:
            output = [s for l, s in db.query.with_entities(db.long_link, db.short_link) if l == url][0]
    '''
    return render_template('link_shorter_page.html')


if __name__ == '__main__':
    app.run(debug=True)    
