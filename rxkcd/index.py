from .db import get_img_url
from .search import run
from .scraper import num_xkcd
from random import randint

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .utils import clean_text

bp = Blueprint('index', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
	if request.method == 'POST':
		query = request.form['query'].split()
		clean_query = [x for x in clean_text(query) if x]
		if not clean_query:
			flash("Invalid query.")
		else:
			return redirect(url_for('index.loading', query=("-".join(clean_query))))
	return render_template('index.html')


@bp.route('/loading/<query>')
def loading(query):
	rand_urls = []
	seen = []
	while len(rand_urls) < 10:
		num = randint(1,num_xkcd)
		if num in seen:
			continue
		comic = get_img_url(num)
		if not comic or 'img_url' not in comic:
			continue
		seen.append(num)
		rand_urls.append(comic['img_url'])
	return render_template('loading.html', query=query, urls=rand_urls)


@bp.route('/search/<query>/', methods=('GET', 'POST'))
def search(query):
	if request.method == 'POST':
		query = request.form['query'].split()
		clean_query = [x for x in clean_text(query) if x]
		if not clean_query:
			flash("Invalid query.")
		else:
			return redirect(url_for('index.loading', query=("-".join(clean_query))))
	keywords = [x for x in clean_text(query.split('-')) if x]
	if keywords:
		comics = run(keywords)
		if comics is None:
			flash("No relevant XKCDs found.")
		else:
			return render_template('search.html', comics=comics, query=query.replace('-',' '))
	return render_template('index.html')