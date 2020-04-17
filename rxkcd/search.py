from .processor import get_relevance, get_related_comics
from .db import get_comic

def run(keywords):
	pos = get_related_comics(keywords)
	cand = [[get_relevance(keywords, get_comic(comic_id)), comic_id] for comic_id in pos]
	cand = sorted(cand,reverse=True)
	num = min(10,len(cand))
	if not cand:
		return None
	return cand[:num]