"""Application factory and database initialization module."""

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os
from typing import Optional

db = SQLAlchemy()

def create_app() -> Flask:
	"""Create and configure the Flask application instance.
	
	Sets up database connection, registers routes and blueprints,
	and initializes the database schema.
	
	Returns:
		Flask: Configured Flask application instance.
		
	Example:
		>>> app = create_app()
		>>> app.run()
	"""

	app = Flask(__name__,
				template_folder='../templates',
				static_folder='../static')

	# Get database URL from environment variable
	database_url: Optional[str] = os.environ.get('DATABASE_URL')

	# Fallback to SQLite if no database URL is provided or during testing
	if not database_url or app.config.get('TESTING'):
		if app.config.get('TESTING'):
			# Skip database setup during testing (handled by conftest.py)
			pass
		else:
			# Use SQLite for local development
			database_url = 'sqlite:///links.db'

	# Fix for older Render.com deployments that use 'postgres://' scheme
	if database_url and database_url.startswith("postgres://"):
		database_url = database_url.replace("postgres://", "postgresql://", 1)

	app.config['SQLALCHEMY_DATABASE_URI'] = database_url
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable overhead

	db.init_app(app)

	# Import view functions to avoid circular imports
	from .app import link_shorter_page, redirect_to_original_link
	app.add_url_rule('/', view_func=link_shorter_page, methods=['GET', 'POST'])
	app.add_url_rule('/<short_link>', view_func=redirect_to_original_link)

	# Register blueprint for additional routes (if any)
	from .app import bp
	app.register_blueprint(bp)

	# Create database tables if they don't exist (skip during testing)
	with app.app_context():
		if not app.config.get('TESTING'):
			db.create_all()
		else:
			pass  # Tables are created by test fixtures

	return app
