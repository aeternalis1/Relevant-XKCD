from .processor import get_relevance, get_related_comics, get_matches
from .db import get_comic
import time
import math

def run(keywords):
	blank = {'id': 0}
	cur_time = time.time()

	keywords = list(set(keywords))
	pos = get_related_comics(keywords)
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
		if time.time()-cur_time > 5:
			yield blank
			cur_time = time.time()

	for i in range(len(cand)):
		val = cand[i][0]
		matches = cand[i][1]
		if top:
			cand[i][0] = val * pow(tot/top, (matches/top-1))

	cand = sorted(cand,reverse=True)
	num = min(10,len(cand))

	for val, matches, comic_id, comic in cand[:num]:
		yield {	'id': comic_id,
				'val': "%.3f" % val,
				'url': comic['img_url'],
				'title': comic['og_title'],
				'title_text': comic['og_ttext']
			  }