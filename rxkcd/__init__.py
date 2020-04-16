import os

from flask import Flask
from flask_pymongo import PyMongo

def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_pyfile('config.py', silent=True)
	mongo = PyMongo(app)

	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	@app.route('/hello')
	def hello():
		return "Hello, World!"

	from . import search
	app.register_blueprint(search.bp)

	return app