"""Core application logic for URL shortening service."""

from flask import Blueprint, render_template, request, redirect, Response
from urllib.parse import urlparse
from app.models import ShortenedLink
from . import db
import hashlib
import random
import string
from typing import Tuple, Optional, Union, Literal


MAX_NUMBER_OF_ATTEMPTS: int = 30
"""Maximum number of attempts to generate a unique short link before failing."""


bp: Blueprint = Blueprint("main", __name__)
"""Flask blueprint for main application routes."""


def hash_link(url: str) -> str:
    """Generate an 8-character hash from a URL with random salt.
    
    Args:
        url: Original URL to hash.
        
    Returns:
        8-character hexadecimal hash string.
        
    Example:
        >>> hash_link("https://example.com")
        'a3f5e8d2'
    """
    salt: str = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    return hashlib.md5((url + salt).encode()).hexdigest()[:8]


def is_valid_link(url: str) -> Union[str, bool]:
    """Validate URL format and length.
    
    Args:
        url: URL to validate. Can be None or empty string.
        
    Returns:
        True if URL is valid, error message string otherwise.
        
    Example:
        >>> is_valid_link("https://example.com")
        True
        >>> is_valid_link("invalid")
        'Некорректный URL :('
    """
    if not url:
        return 'Пожалуйста, введите URL!'
    if len(str(url)) > 2000:
        return 'URL слишком длинный! Поищи короче :)'

    try:
        result: urlparse.ParseResult = urlparse(url=url)
        if not all([result.scheme, result.netloc]) or result.scheme not in ['https', 'http']:
            return 'Некорректный URL :('
        return True
    except (ValueError, AttributeError, TypeError):
        return 'Твой URL не прошел проверку :('


def check_link_existence(url: str,
        field: Literal['original_link', 'short_link']
        ) -> Optional[ShortenedLink]:
    """Check if a link exists in the database by specified field.
    
    Args:
        url: Value to search for (original URL or short code).
        field: Database field to search in ('original_link' or 'short_link').
        
    Returns:
        ShortenedLink object if found, None otherwise.
        
    Example:
        >>> link = check_link_existence("abc123", "short_link")
        >>> if link:
        ...  print(link.original_link)
    """
    try:
        if field == 'original_link':
            result: Optional[ShortenedLink] = ShortenedLink.query.filter_by(original_link=url).first()
        elif field == 'short_link':  
            result: Optional[ShortenedLink] = ShortenedLink.query.filter_by(short_link=url).first()
        return result 
    except Exception as e:
        return None


def increase_number_of_redirections(short_link: str) -> bool:
    """Increment the redirection counter for a short link.
    
    Args:
        short_link: Short link code to update.
        
    Returns:
        True if counter was incremented successfully, False otherwise.
        
    Example:
        >>> increase_number_of_redirections("abc123")
        True
    """
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
    """Handle main page GET and POST requests for URL shortening.
    
    GET: Render the link shortening form.
    POST: Process URL, generate short link, and return result.
    
    Returns:
        Rendered template HTML string or tuple with status code.
        
    Example:
        >>> # POST request with valid URL
        >>> response = link_shorter_page()  # Returns rendered template with short link
    """
    if request.method == 'POST':
        url: Optional[ShortenedLink] = request.form.get('original_link', '').strip()

        check_result: Union[str, bool] = is_valid_link(url)
        if check_result is not True:
            return render_template('link_shorter_page.html',
                error=check_result)

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
    """Redirect short link to original URL and increment visit counter.
    
    Args:
        short_link: Short link code to look up and redirect.
        
    Returns:
        Redirect response to original URL, 404 page if not found,
        or 500 error response on exception.
        
    Example:
        >>> # GET request to /abc123
        >>> response = redirect_to_original_link("abc123")
        >>> response.status_code
        302
    """
    try:
        result: Optional[ShortenedLink] = check_link_existence(short_link, 'short_link')
        if result:
            increase_number_of_redirections(short_link)
            return redirect(result.original_link)
        else:
            return render_template('404.html'), 404
    except Exception as e:
        return Response(str(e.args), status=500)
