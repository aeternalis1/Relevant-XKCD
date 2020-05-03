from .db import get_img_url, get_comic
from .scraper import num_xkcd
from .worker import conn
from .utils import clean_text
from .processor import get_relevance, get_related_comics, get_matches

from random import randint
from rq import Queue, get_current_job
from rq.job import Job
from rq.registry import StartedJobRegistry

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)

import time
import math

bp = Blueprint('index', __name__)

q = Queue('default', connection=conn)


def run(query):
	job = get_current_job()
	keywords = []
	print ("1",time.time())
	job.meta['status'] = 1
	job.save_meta()
	for word in query:
		if word not in keywords:
			keywords.append(word)
	pos = get_related_comics(keywords)
	print (2,time.time())
	job.meta['status'] = 2
	job.save_meta()
	cand = []
	top = 0
	tot = 0

	for comic_id in pos:
		comic = get_comic(comic_id)
		matches = get_matches(keywords, comic)
		val = min(1, get_relevance(keywords, comic) * math.log(matches+10, 10))
		cand.append([val, matches, comic_id, comic])
		top = max(top, matches)
		tot += matches
	print (3,time.time())
	job.meta['status'] = 3
	job.save_meta()
	for i in range(len(cand)):
		matches = cand[i][1]
		if top:
			cand[i][0] *= pow(tot/top, (matches/top-1))

	cand = sorted(cand,reverse=True)
	num = min(10,len(cand))

	res = []

	for val, matches, comic_id, comic in cand[:num]:
		res.append({'id': comic_id,
					'val': "%.3f" % val,
					'url': comic['img_url'],
					'title': comic['og_title'],
					'title_text': comic['og_ttext']
				  })
	job.meta['status'] = 4
	job.save_meta()
	return res


def add_job(keywords):
	try:
		job = Job.fetch("-".join(keywords), connection=conn)
	except:
		job = q.enqueue_call(run, args=(keywords,), result_ttl=5000, failure_ttl=0, job_id="-".join(keywords))
		job.meta['status'] = 0
		job.save_meta()
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
			return redirect(url_for('index.loading', query='-'.join(clean_text(query.split('-')))))
		except:		# job not in queue
			return redirect(url_for('index.loading', query='-'.join(clean_text(query.split('-')))))


@bp.route('/results/<query>', methods=['GET'])
def check_results(query):
	try:
		job = Job.fetch(query, connection=conn)
	except:
		return "nay", 202
	print (job.get_status(), job.meta['status'])
	if job.is_finished:
		print (job.enqueued_at)
		print (job.started_at)
		print (job.ended_at)
		return "job done", 200
	return "nay", 202