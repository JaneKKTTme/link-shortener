from flask import Flask, render_template, request
from pyshorteners import Shortener
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse
import psycopg2
import os

app = Flask(__name__)
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def shorten_link(url):
    shortener = Shortener()
    return shortener.clckru.short(url)

def expand_link(shortened_url):
    shortener = Shortener()
    return shortener.clckru.expand(shortened_url)

def is_valid_url(url):
    try:
        result = urlparse(url=url)
        return all([result.scheme, result.method])
    except:
        return False

@app.route('/', methods=['GET'])
def get_link():
    try:
        url = request.form.get('url', '')
        if not is_valid_url(url):
            return render_template('link_shorter_page.html', output=is_valid_url(url))
    except:
            return render_template('link_shorter_page.html', output='ERROR')


@app.route('/', methods=['GET', 'POST'])
def link_shorter_page():
    output = None
    url = get_link()

    if request.method == 'POST':
        try:
            output = shorten_link(url)
            db.execute(
                "INSERT INTO shortened_links (long_link, short_link) VALUES (?, ?)", 
                (url, output)
            )
            db.commit()
        except db.IntegrityError:
            #output = [s for l, s in db.query.with_entities(db.long_link, db.short_link) if l == url][0]
            output = '12345'
    return render_template('link_shorter_page.html', output=output)


if __name__ == '__main__':
    app.run(debug=True)    
