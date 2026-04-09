"""Integration tests for complete URL shortening workflows."""

import pytest
from app.models import ShortenedLink


class TestIntegration:
    """Test suite for end-to-end functionality and real-world scenarios."""
    
    def test_full_workflow(self, client, db):
        """Test complete workflow: create, redirect, and track link.
        
        Verifies:
        1. Short link creation
        2. Redirection to original URL
        3. Visit counter increment
        4. Idempotent link creation (same URL returns existing link)
        """
        original_url = 'https://integration-test.com/some/very/long/path'
        
        # Create short link
        response = client.post('/', data={
            'original_link': original_url
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        response_text = response.data.decode('utf-8')
        
        link = ShortenedLink.query.filter_by(original_link=original_url).first()
        assert link is not None
        short_code = link.short_link
        
        # First redirect
        redirect_response = client.get(f'/{short_code}', follow_redirects=False)
        assert redirect_response.status_code == 302
        assert redirect_response.location == original_url
        
        db.session.refresh(link)
        assert link.number_of_redirections == 1
        
        # Second redirect
        client.get(f'/{short_code}')
        db.session.refresh(link)
        assert link.number_of_redirections == 2
        
        # Create same URL again - should return existing link
        response2 = client.post('/', data={
            'original_link': original_url
        }, follow_redirects=True)
        
        assert response2.status_code == 200
        links = ShortenedLink.query.filter_by(original_link=original_url).all()
        assert len(links) == 1
    
    def test_concurrent_requests_handling(self, client, db):
        """Test that concurrent requests for same URL don't create duplicate links.
        
        Simulates multiple simultaneous requests to ensure database
        constraints prevent duplicate short links for the same URL.
        """
        import threading
        
        results = []
        
        def create_link():
            response = client.post('/', data={
                'original_link': 'https://concurrent-test.com'
            }, follow_redirects=True)
            results.append(response.status_code)
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_link)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert all(status == 200 for status in results)
        
        links = ShortenedLink.query.filter_by(original_link='https://concurrent-test.com').all()
        assert len(links) == 1
    
    def test_multiple_links_creation(self, client, db):
        """Test creating multiple different links successfully."""
        urls = [
            'https://test1.com',
            'https://test2.com',
            'https://test3.com',
        ]
        
        for url in urls:
            response = client.post('/', data={'original_link': url}, follow_redirects=True)
            assert response.status_code == 200
        
        for url in urls:
            link = ShortenedLink.query.filter_by(original_link=url).first()
            assert link is not None
            assert link.short_link is not None
            assert len(link.short_link) == 8
