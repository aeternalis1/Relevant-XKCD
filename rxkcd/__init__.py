import os

from flask import Flask
from .instance.config import SECRET_KEY

def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_pyfile('config.py', silent=True)
	app.secret_key = SECRET_KEY

	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	from . import index
	app.register_blueprint(index.bp)

	return app