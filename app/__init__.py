from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

db = SQLAlchemy()

def create_app():
	app = Flask(__name__,
				template_folder='../templates',
				static_folder='../static')

	database_url = os.environ.get('DATABASE_URL')
	if database_url and database_url.startswith("postgres://"):
	    database_url = database_url.replace("postgres://", "postgresql://", 1)

	app.config['SQLALCHEMY_DATABASE_URI'] = database_url
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

	db.init_app(app)

	from .app import link_shorter_page, redirect_to_original_link
	app.add_url_rule('/', view_func=link_shorter_page, methods=['GET', 'POST'])
	app.add_url_rule('/<short_link>', view_func=redirect_to_original_link)

	from .app import bp
	app.register_blueprint(bp)

	with app.app_context():
		db.create_all()

	return app