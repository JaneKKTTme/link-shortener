import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db as _db
from app.models import ShortenedLink

@pytest.fixture
def app():
	db_fd, db_path = tempfile.mkstemp()

	app = create_app()

	app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}?check_same_thread=False'
	app.config['TESTING'] = True
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	app.config['WTF_CSRF_ENABLED'] = False
	app.config['SERVER_NAME'] = 'localhost.localdomain'

	with app.app_context():
		_db.create_all()

		from sqlalchemy import text
		_db.session.execute(text("PRAGMA journal_mode=WAL"))
		_db.session.commit()

	yield app

	with app.app_context():
		_db.drop_all()

	os.close(db_fd)
	os.unlink(db_path)

@pytest.fixture
def client(app):
	return app.test_client()

@pytest.fixture
def db(app):
	with app.app_context():
		yield _db
		_db.session.remove()

@pytest.fixture
def sample_link(db):
	link = ShortenedLink(
		original_link='https://example.com/test',
		short_link='example1'
	)
	db.session.add(link)
	db.session.commit()

	return link