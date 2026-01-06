from flask import Flask, render_template, request, redirect, Response
from urllib.parse import urlparse
from api.models import ShortenedLink
from link-shoter import db, app
import os
import hashlib


database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def hash_link(url):
    salt = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    return hashlib.md5((url + salt).encode()).hexdigest()[:8]


def is_valid_url(url):
    try:
        result = urlparse(url=url)
        if not all([result.scheme, result.netloc]):
            return False
        if result.scheme not in ['https', 'http']:
            return False
        return True
    except Exception:
        return False


def is_existed(url, field):
    try:
        if field == 'original_link':
            result = ShortenedLink.query.filter_by(original_link=url).first()
        elif field == 'short_link':  
            result = ShortenedLink.query.filter_by(short_link=url).first()
        return result 
    except Exception:
        return False


@app.route('/', methods=['GET', 'POST'])
def link_shorter_page():
    if request.method == 'POST':
        url = request.form.get('original_link', '').strip()
        if not url:
            return render_template('link_shorter_page.html', 
                                 error='Пожалуйста, введите URL!')
        if len(str(url)) > 2000:
            return render_template('link_shorter_page.html',
                error="URL слишком длинный :(\nПоищи короче :)")
        if not is_valid_url(url):
            return render_template('link_shorter_page.html',
                error='Некорректный URL :(')

        try:
            #existing_link = ShortenedLink.query.filter_by(original_link=url).first()
            existing_link = is_existed(url, 'original_link')
            if existing_link:
                return render_template('link_shorter_page.html',
                    original_link=url,
                    output='https://link-shorter-si7x.onrender.com/' + existing_link.short_link)

        except Exception as e:
            return render_template('link_shorter_page.html',
                error='Возникли технические шоколадки: ' + str(e))

        try:
            hashed_link = hash_link(url)
            while is_existed(hashed_link, 'short_link'):
                hashed_link = hash_link(url)
            output = 'https://link-shorter-si7x.onrender.com/' + hashed_link
            shortened_link = ShortenedLink(
                original_link=url,
                short_link = hashed_link,
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

def get_long_link(short_link):
    try:
        long_link = ShortenedLink.query.filter_by(short_link=short_link).first()
        if long_link:
            return long_link.original_link
    except Exception as e:
        raise e

@app.route('/<short_link>')
def redirect_to_original_link(short_link):
    try:
        long_link = get_long_link(short_link)
        if long_link:
            return redirect(long_link)
        else:
            return render_template('404.html'), 404
    except Exception as e:
        return Response(str(e.args), status=500)


if __name__ == '__main__':
    app.run(debug=os.environ.get('DEBUG', 'False').lower() == 'true')    
