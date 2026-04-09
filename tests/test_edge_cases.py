"""Edge case tests for URL shortening service."""

import pytest
from app.app import MAX_NUMBER_OF_ATTEMPTS
from app.models import ShortenedLink


class TestEdgeCases:
    """Test suite for edge cases and special scenarios."""
    
    def test_unicode_url(self, client, db):
        """Test URL with Unicode characters is handled correctly.
        
        Verifies that URLs containing non-ASCII characters (Cyrillic)
        are properly stored and processed.
        """
        unicode_url = 'https://example.com/путь/с/русскими/символами'
        
        response = client.post('/', data={
            'original_link': unicode_url
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        link = ShortenedLink.query.filter_by(original_link=unicode_url).first()
        assert link is not None
    
    def test_url_with_port(self, client, db):
        """Test URL with custom port number is handled correctly."""
        url_with_port = 'https://example.com:8080/path'
        
        response = client.post('/', data={
            'original_link': url_with_port
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        link = ShortenedLink.query.filter_by(original_link=url_with_port).first()
        assert link is not None
    
    def test_url_with_fragment(self, client, db):
        """Test URL with fragment/hash identifier is handled correctly."""
        url_with_fragment = 'https://example.com/page#section'
        
        response = client.post('/', data={
            'original_link': url_with_fragment
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        link = ShortenedLink.query.filter_by(original_link=url_with_fragment).first()
        assert link is not None
    
    def test_url_with_special_characters(self, client, db):
        """Test URL with URL-encoded special characters is handled correctly."""
        special_url = 'https://example.com/path?param=value&foo=bar&baz=hello%20world'
        
        response = client.post('/', data={
            'original_link': special_url
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        link = ShortenedLink.query.filter_by(original_link=special_url).first()
        assert link is not None
    
    def test_localhost_url(self, client, db):
        """Test localhost URL is accepted (useful for development)."""
        localhost_url = 'http://localhost:5000'
        
        response = client.post('/', data={
            'original_link': localhost_url
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        link = ShortenedLink.query.filter_by(original_link=localhost_url).first()
        assert link is not None
    
    def test_ip_address_url(self, client, db):
        """Test IP address URL is accepted."""
        ip_url = 'http://127.0.0.1:8000'
        
        response = client.post('/', data={
            'original_link': ip_url
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        link = ShortenedLink.query.filter_by(original_link=ip_url).first()
        assert link is not None
    
    def test_very_similar_urls(self, client, db):
        """Test that similar URLs generate different short codes."""
        url1 = 'https://example.com/path1'
        url2 = 'https://example.com/path2'
        
        client.post('/', data={'original_link': url1})
        client.post('/', data={'original_link': url2})
        
        link1 = ShortenedLink.query.filter_by(original_link=url1).first()
        link2 = ShortenedLink.query.filter_by(original_link=url2).first()
        
        assert link1 is not None
        assert link2 is not None
        assert link1.short_link != link2.short_link
    
    def test_max_attempts_constant(self):
        """Test MAX_NUMBER_OF_ATTEMPTS constant has correct type and value."""
        assert isinstance(MAX_NUMBER_OF_ATTEMPTS, int)
        assert MAX_NUMBER_OF_ATTEMPTS > 0
        assert MAX_NUMBER_OF_ATTEMPTS == 30
