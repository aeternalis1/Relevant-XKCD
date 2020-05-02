from db import get_img_url
from search import run
from scraper import num_xkcd
from worker import conn
from utils import clean_text

from random import randint
from rq import Queue
from rq.job import Job
from rq.registry import StartedJobRegistry

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)

import time

bp = Blueprint('index', __name__)

q = Queue('default', connection=conn)


def add_job(keywords):
	try:
		job = Job.fetch("-".join(keywords), connection=conn)
	except:
		job = q.enqueue_call(run, args=(keywords,), result_ttl=5000, failure_ttl=0, job_id="-".join(keywords))
	return


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
	add_job(clean_text(query.split('-')))
	return render_template('loading.html', query=query, urls=rand_urls)


@bp.route('/search/<query>', methods=('GET', 'POST'))
def search(query):
	if request.method == 'POST':
		new_query = request.form['query'].split()
		clean_query = [x for x in clean_text(new_query) if x]
		if not clean_query:
			flash("Invalid query.")
			return render_template('search.html', comics=comics, query=query.replace('-',' '))
		else:
			return redirect(url_for('index.loading', query=("-".join(clean_query))))
	else:
		try:
			job = Job.fetch(query, connection=conn)
			if job.is_finished:
				return render_template('search.html', comics=job.result, query=query.replace('-',' '))
			elif job.get_status() == 'failed':
				add_job(clean_text(query.split('-')))
			return redirect(url_for('index.loading', query='-'.join(clean_text(query.split('-')))))
		except:		# job not in queue
			return redirect(url_for('index.loading', query='-'.join(clean_text(query.split('-')))))


@bp.route('/results/<query>', methods=['GET'])
def check_results(query):
	try:
		job = Job.fetch(query, connection=conn)
		if job.is_finished:
			return "job finished", 200
		return "nay", 202
	except:		# job not in queue
		return "nay", 202