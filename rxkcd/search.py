import functools

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from utils import clean_text

bp = Blueprint('index', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
	if request.method == 'POST':
		query = request.form['query'].split()
		clean_query = [x for x in clean_text(query) if x]
		if not clean_query:
			flash("Invalid query.")
		else:
			return redirect(url_for('index.search', query=("-".join(clean_query))))
	return render_template('index.html')


@bp.route('/search/<query>', methods=('GET', 'POST'))
def search(query):
	keywords = [clean_text(x) for x in query.split('-') if clean_text(x)]
	if keywords:
		
	return render_template('index.html')