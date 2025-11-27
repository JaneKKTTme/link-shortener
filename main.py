from flask import Flask, render_template, request
from pyshorteners import Shortener
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse

app = Flask(__name__)

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

def init_db():
    db = get_db()
    with app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode(utf8))

@app.route('/', methods=['GET', 'POST'])
def link_shorter_page():
    db = init_db()
    session = Session()
    output = None
    if not is_valid_url(url):
        return render_template('link_shorter_page.html', output=is_valid_url(url))

    if request.method == 'POST':
        url = request.form.get('url', '')
        try:
            output = shorten_link(url)
            db.execute(
                "INSERT INTO shortened_links (long_link, short_link) VALUES (?, ?)", 
                (url, output)
            )
            db.commit()
        except db.IntegrityError:
            output = [s for l, s in db.query.with_entities(db.long_link, db.short_link) if l == url][0]
    return render_template('link_shorter_page.html', output=output)


if __name__ == '__main__':
    app.run(debug=True)    
