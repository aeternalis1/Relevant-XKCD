from .processor import get_relevance, get_related_comics
from .db import get_comic
import time

def run(keywords):
	start = time.time()
	pos = get_related_comics(keywords)
	start = time.time()
	cand = [[get_relevance(keywords, get_comic(comic_id)), comic_id] for comic_id in pos]
	cand = sorted(cand,reverse=True)
	num = min(10,len(cand))
	if not cand:
		return None
	res = []
	for val, comic_id in cand[:num]:
		comic = get_comic(comic_id)
		res.append({'id': comic_id,
					'val': "%.3f" % val,
					'url': comic['img_url'],
					'title': comic['og_title'],
					'title_text': comic['og_ttext']
					})
	return res