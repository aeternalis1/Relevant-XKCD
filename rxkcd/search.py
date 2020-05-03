from rq import get_current_job

import time
import math

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