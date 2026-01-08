from flask import Blueprint, render_template, request, redirect, Response
from urllib.parse import urlparse
from app.models import ShortenedLink
from . import db
import hashlib
import random
import string
from typing import Tuple, Optional, Union, Literal, Callable, Any, Dict


MAX_NUMBER_OF_ATTEMPTS: int = 30


bp: Blueprint = Blueprint("main", __name__)


def hash_link(url: str) -> str:
    salt: str = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    return hashlib.md5((url + salt).encode()).hexdigest()[:8]


def is_valid_link(url: str) -> bool:
    try:
        result: urlparse.ParseResult = urlparse(url=url)
        if not all([result.scheme, result.netloc]):
            return False
        if result.scheme not in ['https', 'http']:
            return False
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def check_link_existence(url: str,
        field: Literal['original_link', 'short_link']
        ) -> Optional[ShortenedLink]:
    try:
        if field == 'original_link':
            result: Optional[ShortenedLink] = ShortenedLink.query.filter_by(original_link=url).first()
        elif field == 'short_link':  
            result: Optional[ShortenedLink] = ShortenedLink.query.filter_by(short_link=url).first()
        return result 
    except Exception as e:
        return None


def increase_number_of_redirections(short_link: str) -> bool:
    shortened_link: Optional[ShortenedLink] = check_link_existence(short_link, 'short_link')
    if not shortened_link:
        return False

    try:
        shortened_link.number_of_redirections = shortened_link.number_of_redirections + 1
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False


def link_shorter_page() -> Union[str, Tuple[str, int]]:
    if request.method == 'POST':
        url: Optional[ShortenedLink] = request.form.get('original_link', '').strip()
        
        if not url:
            return render_template('link_shorter_page.html', 
                                 error='Пожалуйста, введите URL!')
        if len(str(url)) > 2000:
            return render_template('link_shorter_page.html',
                error="URL слишком длинный! Поищи короче :)")
        if not is_valid_link(url):
            return render_template('link_shorter_page.html',
                error='Некорректный URL :(')

        try:
            result:  Optional[ShortenedLink] = check_link_existence(url, 'original_link')
            if result:
                return render_template('link_shorter_page.html',
                    original_link=url,
                    output='https://link-shorter-si7x.onrender.com/' + result.short_link)
        except Exception as e:
            return render_template('link_shorter_page.html',
                error='Возникли технические шоколадки: ' + str(e))

        try:
            hashed_link: str = hash_link(url)
            number_of_attempts: int = 0
            while check_link_existence(hashed_link, 'short_link') and number_of_attempts < MAX_NUMBER_OF_ATTEMPTS:
                hashed_link = hash_link(url)
                number_of_attempts += 1
            if number_of_attempts >= MAX_NUMBER_OF_ATTEMPTS:
                return render_template('link_shorter_page.html',
                    error='Не удалось сгенерировать уникальную короткую ссылку. Попробуйте еще раз :)')
            output: str = 'https://link-shorter-si7x.onrender.com/' + hashed_link
            shortened_link: ShortenedLink = ShortenedLink(
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


def redirect_to_original_link(short_link: str) -> Union[Response, Tuple[str, int]]:
    try:
        result: Optional[ShortenedLink] = check_link_existence(short_link, 'short_link')
        if result:
            increase_number_of_redirections(short_link)
            return redirect(result.original_link)
        else:
            return render_template('404.html'), 404
    except Exception as e:
        return Response(str(e.args), status=500)
