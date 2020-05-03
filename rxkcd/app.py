import os

from flask import Flask
from instance.config import SECRET_KEY
import spacy

def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_pyfile('config.py', silent=True)
	app.secret_key = SECRET_KEY

	from processor import nlp 	# makes spacy load processed during init

	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	import index
	app.register_blueprint(index.bp)

	return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port)