from .processor import get_relevance, get_related_comics
from .db import get_comic
from .scraper import get_title, get_ttext
import time

def run(keywords):
	start = time.time()
	pos = get_related_comics(keywords)
	print (time.time()-start)
	start = time.time()
	cand = [[get_relevance(keywords, get_comic(comic_id)), comic_id] for comic_id in pos]
	print (time.time()-start)
	cand = sorted(cand,reverse=True)
	num = min(10,len(cand))
	if not cand:
		return None
	res = []
	for val, comic_id in cand[:num]:
		comic = get_comic(comic_id)
		res.append({'id': comic_id,
					'val': round(val,3),
					'url': comic['img_url'],
					'title': get_title(comic_id),
					'title_text': get_ttext(comic_id)
					})
	return res