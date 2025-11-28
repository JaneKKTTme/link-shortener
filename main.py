from flask import Flask, render_template, request
from pyshorteners import Shortener
from urllib.parse import urlparse
from model import *

app = Flask(__name__)
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
init_db()


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
            existing_link = ShortenedLink.query.filter_by(long_link=url).first()
            if existing_link:
                return render_template('link_shorter_page.html',
                    output=existing_link.short_link)
        except Exception as e:
            return render_template('link_shorter_page.html',
                error=e)

        try:
            output = shorten_link(url)
            shortened_link = ShortenedLink(
                long_link = url,
                short_link = output,
            )
            db.session.add(shortened_link)
            db.session.commit()
            #output = ShortenedLink.query.filter_by(long_link=url).first()
            return render_template('link_shorter_page.html',
                output=output)
        except Exception as e:
            db.session.rollback()
            return render_template('link_shorter_page.html',
                error='ERROR:'+ db.session.execute(db.select(ShortenedLink).filter_by(long_link=url)).scalar_one())
    
    return render_template('link_shorter_page.html')


if __name__ == '__main__':
    app.run(debug=True)    
