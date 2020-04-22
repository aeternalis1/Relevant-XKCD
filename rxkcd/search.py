from .processor import get_relevance, get_related_comics
from .db import get_comic
import time

def run(keywords):
	keywords = list(set(keywords))
	pos = get_related_comics(keywords)
	cand = []
	for comic_id in pos:
		comic = get_comic(comic_id)
		cand.append([get_relevance(keywords, comic), comic_id, comic])	# comic_id breaks ties
	cand = sorted(cand,reverse=True)
	num = min(10,len(cand))
	if not cand:
		return None
	res = []
	for val, comic_id, comic in cand[:num]:
		res.append({'id': comic_id,
					'val': "%.3f" % val,
					'url': comic['img_url'],
					'title': comic['og_title'],
					'title_text': comic['og_ttext']
					})
	return res