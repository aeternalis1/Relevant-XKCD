from db import get_img_url, get_comic, get_recent
from scraper import num_xkcd
from worker import conn
from utils import clean_text
from processor import get_relevance, get_related_comics, get_matches

from random import randint
from rq import Queue
from rq.job import Job
from rq.registry import StartedJobRegistry

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)

import time
import math
from apscheduler.schedulers.background import BackgroundScheduler

bp = Blueprint('index', __name__)

q = Queue('default', connection=conn)


def run(query, stype):
	keywords = []
	for word in query:
		if word not in keywords:
			keywords.append(word)
	pos = get_related_comics(keywords)

	if stype == 'normal':
		cand = [[x[0]]+[0]+[x[1]]+[get_comic(x[1])] for x in pos]
	else:
		pos = [x[1] for x in pos]
		cand = []
		top = 0
		tot = 0

		for comic_id in pos:
			comic = get_comic(comic_id)
			print (comic_id, comic)
			matches = get_matches(keywords, comic)
			val = min(1, get_relevance(keywords, comic) * math.log(matches+10, 10))
			cand.append([val, matches, comic_id, comic])
			top = max(top, matches)
			tot += matches

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

	return res


def add_job(keywords, stype):
	try:
		job = Job.fetch(stype+"/"+"-".join(keywords), connection=conn)
	except:
		job = q.enqueue_call(run, args=(keywords, stype,), result_ttl=5000, failure_ttl=0, job_id=stype+"/"+"-".join(keywords))
	return


@bp.route('/', methods=('GET', 'POST'))
def index():
	if request.method == 'POST':
		query = request.form['query'].split()
		clean_query = [x for x in clean_text(query) if x]
		if not clean_query:
			flash("Invalid query.")
		else:
			stype = request.form['search_button'].split()[0].lower()
			return redirect(url_for('index.loading', stype=stype, query=("-".join(clean_query))))
	return render_template('index.html')


@bp.route('/loading/<stype>/<query>')
def loading(stype, query):
	rand_urls = []
	rand_ttexts = []
	seen = []
	while len(rand_urls) < 10:
		num = randint(1,num_xkcd)
		if num in seen:
			continue
		comic = get_comic(num)
		if not comic or 'img_url' not in comic:
			continue
		seen.append(num)
		rand_urls.append(comic['img_url'])
		rand_ttexts.append(comic['og_ttext'])
	add_job(clean_text(query.split('-')), stype)
	return render_template('loading.html', stype=stype, query=query, urls=rand_urls, ttexts=rand_ttexts)


@bp.route('/search/<stype>/<query>', methods=('GET', 'POST'))
def search(stype, query):
	if request.method == 'POST':
		new_query = request.form['query'].split()
		clean_query = [x for x in clean_text(new_query) if x]
		if not clean_query:
			flash("Invalid query.")
			return render_template('search.html', comics=comics, query=query.replace('-',' '))
		else:
			stype = request.form['search_button'].split()[0].lower()
			return redirect(url_for('index.loading', stype=stype, query=("-".join(clean_query))))
	else:
		try:
			job = Job.fetch(stype+'/'+query, connection=conn)
			if job.is_finished:
				if job.result:
					return render_template('search.html', comics=job.result, query=query.replace('-',' '), res=1)
				else:
					return render_template('search.html', query=query.replace('-',' '), res=0)
			return redirect(url_for('index.loading', stype=stype, query='-'.join(clean_text(query.split('-')))))
		except:		# job not in queue
			return redirect(url_for('index.loading', stype=stype, query='-'.join(clean_text(query.split('-')))))


@bp.route('/results/<stype>/<query>', methods=['GET'])
def check_results(stype, query):
	try:
		job = Job.fetch(stype+'/'+query, connection=conn)
	except:
		return "nay", 202
	if job.is_finished:
		return "job done", 200
	return "nay", 202


sched = BackgroundScheduler({'apscheduler.timezone': 'America/Toronto'}, daemon=True)

@sched.scheduled_job('interval', hours=12)
def timed_update():
	job = q.enqueue_call(get_recent, result_ttl=0, failure_ttl=0, job_id="check_recent")