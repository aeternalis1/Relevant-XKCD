from scraper import get_info, scrape_pages
from processor import get_relevance, get_related_comics
from nltk.corpus import wordnet
from database import reset_data, retrieve_data
import time

def query(keywords, comics, wordbank, start):
	print (time.time()-start)
	pos = get_related_comics(keywords, wordbank)
	print (time.time()-start)
	cand = [[get_relevance(keywords, comics[str(comic_id)]), comic_id] for comic_id in pos]
	print (time.time()-start)
	cand = sorted(cand,reverse = True)
	return cand[0]


def main():
	#reset_data()
	start = time.time()
	comics, wordbank = retrieve_data()

	keywords = ["correlation","causation"]
	print ("HERE")
	print (query(keywords, comics, wordbank, start))
	print ("TOTAL TIME",time.time()-start)


if __name__ == '__main__':
	main()

'''
Filter comics first by keywords, narrowing search pool (preliminary)
- use wordnet to get synonyms of queried key words, then match with words in the bank
- compare words in top N relevant comics to query words using spacy

Then, parse the filtered comics for exact matches (e.g. "Star Wars")
- Give high priority to exact matches of multiple search terms


'''