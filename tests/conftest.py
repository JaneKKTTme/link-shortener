"""Pytest fixtures and configuration for testing."""

import pytest
import os
import tempfile
import sys

# Add project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db as _db
from app.models import ShortenedLink


@pytest.fixture
def app():
	"""Create and configure a Flask application instance for testing.
	
	Sets up an isolated test database using SQLite in memory.
	
	Yields:
		Flask: Configured Flask application with test database.
		
	Example:
		>>> def test_something(app):
		...		with app.app_context():
		...		# Test database operations
	"""
	# Create temporary database file
	db_fd, db_path = tempfile.mkstemp()

	app = create_app()

	# Override configuration for testing
	app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}?check_same_thread=False'
	app.config['TESTING'] = True  # Disables error catching during testing
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing forms
	app.config['SERVER_NAME'] = 'localhost.localdomain'  # Required for url_for

	# Initialize database schema
	with app.app_context():
		_db.create_all()

		# Enable WAL mode for better concurrent test performance
		from sqlalchemy import text
		_db.session.execute(text("PRAGMA journal_mode=WAL"))
		_db.session.commit()

	yield app

	# Cleanup: drop tables and remove temporary database file
	with app.app_context():
		_db.drop_all()

	os.close(db_fd)
	os.unlink(db_path)


@pytest.fixture
def client(app):
	"""Create a test client for making HTTP requests.
	
	Args:
		app: Flask application fixture.
		
	Returns:
		FlaskClient: Test client for making requests to the application.
		
	Example:
		>>> def test_homepage(client):
		...		response = client.get('/')
		...		assert response.status_code == 200
	"""
	return app.test_client()


@pytest.fixture
def db(app):
	"""Provide database session for testing.
	
	Args:
		app: Flask application fixture.
		
	Yields:
		SQLAlchemy: Database instance with active application context.
		
	Example:
		>>> def test_database_operation(db):
		...		link = ShortenedLink(...)
		...		db.session.add(link)
		...		db.session.commit()
	"""
	with app.app_context():
		yield _db
		_db.session.remove()


@pytest.fixture
def sample_link(db):
	"""Create a sample link record in the test database.
	
	Args:
		db: Database fixture.
		
	Returns:
		ShortenedLink: Created link instance with test data.
		
	Example:
		>>> def test_with_sample_link(sample_link):
		...		assert sample_link.short_link == "example1"
	"""
	link = ShortenedLink(
		original_link='https://example.com/test',
		short_link='example1'
	)
	db.session.add(link)
	db.session.commit()

	return link
