from flask import Flask, render_template, request
from pyshorteners import Shortener
from urllib.parse import urlparse
from model import *
import os

app = Flask(__name__)

database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    init_db(app)


def shorten_link(url):
    try:
        shortener = Shortener()
        return shortener.clckru.short(url)
    except Exception as e:
        raise Exception(f'Ошибка сокращения: {str(e)}')

def expand_link(url):
    try:
        shortener = Shortener()
        return shortener.clckru.expand(url)
    except Exception as e:
        raise Exception(f'Ошибка декодирования: {str(e)}')


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
        url = request.form.get('original_link', '').strip()
        if not url:
            return render_template('link_shorter_page.html', 
                                 error='Пожалуйста, введите URL!')
        if not is_valid_url(url):
            return render_template('link_shorter_page.html',
                error='Некорректный URL :(')

        try:
            existing_link = ShortenedLink.query.filter_by(original_link=url).first()
            if existing_link:
                return render_template('link_shorter_page.html',
                    original_link=url,
                    output=existing_link.short_link)

        except Exception as e:
            return render_template('link_shorter_page.html',
                error='Возникли технические шоколадки: ' + str(e))

        try:
            output = shorten_link(url)
            shortened_link = ShortenedLink(
                short_link = output,
            )
            db.session.add(shortened_link)
            db.session.commit()
            return render_template('link_shorter_page.html',
                original_link=url,
                output=output)
        except Exception as e:
            db.session.rollback()
            return render_template('link_shorter_page.html',
                error='База данных вышла на перекур :(')
    
    return render_template('link_shorter_page.html')


if __name__ == '__main__':
    app.run(debug=os.environ.get('DEBUG', 'False').lower() == 'true')    
