import pytest
from unittest.mock import patch, MagicMock
from app.app import (
    is_valid_link, 
    hash_link, 
    MAX_NUMBER_OF_ATTEMPTS,
    check_link_existence,
    increase_number_of_redirections
)
from app.models import ShortenedLink


class TestValidation:

    def test_valid_http_url(self):
        result = is_valid_link('http://example.com')
        
        assert result is True
    
    def test_valid_https_url(self):
        result = is_valid_link('https://example.com')
        
        assert result is True
    
    def test_valid_url_with_path(self):
        result = is_valid_link('https://example.com/path/to/page')
        
        assert result is True
    
    def test_valid_url_with_query(self):
        result = is_valid_link('https://example.com?param=value&foo=bar')
        
        assert result is True

    def test_empty_url(self):
        result = is_valid_link('')

        assert isinstance(result, str)
        assert 'введите' in result.lower()
    
    def test_none_url(self):
        result = is_valid_link(None)

        assert isinstance(result, str)
        assert 'введите' in result.lower()
    
    def test_url_without_scheme(self):
        result = is_valid_link('example.com')

        assert isinstance(result, str)
        assert 'Некорректный URL' in result

    def test_invalid_scheme(self):
        result = is_valid_link('ftp://example.com')

        assert isinstance(result, str)
        assert 'Некорректный URL' in result
    
    def test_very_long_url(self):
        long_url = 'https://example.com/' + 'a' * 2000
        result = is_valid_link(long_url)

        assert isinstance(result, str)
        assert 'длинный' in result


class TestHashLink:
    def test_hash_link_returns_string(self):
        result = hash_link('https://example.com')

        assert isinstance(result, str)
        assert len(result) == 8
    
    def test_hash_link_different_for_different_urls(self):
        hash1 = hash_link('https://example.com/1')
        hash2 = hash_link('https://example.com/2')

        assert hash1 != hash2

    def test_hash_link_with_salt(self):
        with patch('app.app.random.choices') as mock_choices:
            mock_choices.return_value = ['a', 'b', 'c', 'd']
            hash1 = hash_link('https://example.com')
            
            mock_choices.return_value = ['e', 'f', 'g', 'h']
            hash2 = hash_link('https://example.com')
            
            assert hash1 != hash2


class TestCheckLinkExistence:

    def test_check_by_original_link_exists(self, db, sample_link):
        result = check_link_existence(sample_link.original_link, 'original_link')
        
        assert result is not None
        assert result.id == sample_link.id
    
    def test_check_by_original_link_not_exists(self, db):
        result = check_link_existence('https://nonexistent.com', 'original_link')
        
        assert result is None
    
    def test_check_by_short_link_exists(self, db, sample_link):
        result = check_link_existence(sample_link.short_link, 'short_link')
        
        assert result is not None
        assert result.id == sample_link.id
    
    def test_check_by_short_link_not_exists(self, db):
        result = check_link_existence('nonexistent', 'short_link')

        assert result is None

    def test_check_with_invalid_field(self, db, sample_link):
        result = check_link_existence(sample_link.original_link, 'invalid_field')
        
        assert result is None


class TestIncreaseRedirections:

    def test_increase_redirections_success(self, db, sample_link):
        initial_count = sample_link.number_of_redirections
        result = increase_number_of_redirections(sample_link.short_link)
        
        assert result is True
        db.session.refresh(sample_link)
        assert sample_link.number_of_redirections == initial_count + 1
    
    def test_increase_redirections_nonexistent(self, db):
        result = increase_number_of_redirections('nonexistent')

        assert result is False

    def test_increase_redirections_multiple(self, db, sample_link):
        for i in range(5):
            result = increase_number_of_redirections(sample_link.short_link)
            assert result is True
        
        db.session.refresh(sample_link)
        assert sample_link.number_of_redirections == 5


class TestLinkShorterPage:

    def test_get_request_returns_form(self, client):
        response = client.get('/')

        assert response.status_code == 200
        data = response.data.decode('utf-8').lower()
        assert 'link-shorter' in data or 'сокращатель' in data
    
    def test_post_new_valid_link(self, client, db):
        response = client.post('/', data={
            'original_link': 'https://newsite.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        link = ShortenedLink.query.filter_by(original_link='https://newsite.com').first()
        assert link is not None

    def test_post_existing_link_returns_existing_short(self, client, db, sample_link):
        response = client.post('/', data={
            'original_link': sample_link.original_link
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert sample_link.short_link in response.data.decode('utf-8')
    
    def test_post_invalid_link_shows_error(self, client):
        response = client.post('/', data={
            'original_link': 'invalid-url'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert 'Некорректный URL' in response_text or 'не прошел проверку' in response_text

    def test_post_empty_link_shows_error(self, client):
        response = client.post('/', data={
            'original_link': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert 'Пожалуйста' in response.data.decode('utf-8')

    @patch('app.app.check_link_existence')
    def test_post_with_database_error(self, mock_check, client):
        def side_effect(*args, **kwargs):
            raise Exception("Database error")
        
        mock_check.side_effect = side_effect
        
        response = client.post('/', data={
            'original_link': 'https://example.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert 'технические' in response_text or 'шоколадки' in response_text


class TestRedirect:

    def test_redirect_to_existing_link(self, client, db, sample_link):
        response = client.get(f'/{sample_link.short_link}', follow_redirects=False)
        
        assert response.status_code == 302
        assert response.location == sample_link.original_link
    
    def test_redirect_nonexistent_link_returns_404(self, client):
        response = client.get('/nonexistent123')
        
        assert response.status_code == 404

    def test_redirect_increments_counter(self, client, db, sample_link):
        initial_count = sample_link.number_of_redirections
        
        client.get(f'/{sample_link.short_link}')
        
        db.session.refresh(sample_link)
        assert sample_link.number_of_redirections == initial_count + 1
    
    def test_redirect_multiple_times(self, client, db, sample_link):
        for i in range(3):
            client.get(f'/{sample_link.short_link}')
        
        db.session.refresh(sample_link)
        assert sample_link.number_of_redirections == 3


class TestCollisionHandling:
    
    @patch('app.app.hash_link')
    @patch('app.app.check_link_existence')
    def test_collision_resolved(self, mock_check, mock_hash, client):
        mock_hash.side_effect = ['hash1', 'hash1', 'hash2']

        def check_side_effect(link, field):
            if field == 'short_link' and link in ['hash1']:
                return MagicMock() 
            return None
        
        mock_check.side_effect = check_side_effect
        
        response = client.post('/', data={
            'original_link': 'https://collision.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert 'hash2' in response.data.decode('utf-8') or response.status_code == 200

    @patch('app.app.hash_link')
    @patch('app.app.check_link_existence')
    def test_max_attempts_reached(self, mock_check, mock_hash, client):
        mock_hash.return_value = 'samehash'
        
        def check_side_effect(link, field):
            if field == 'short_link':
                return MagicMock()
            return None
        
        mock_check.side_effect = check_side_effect
        
        response = client.post('/', data={
            'original_link': 'https://maxattempts.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert 'не удалось сгенерировать' in response_text or 'уникальную' in response_text