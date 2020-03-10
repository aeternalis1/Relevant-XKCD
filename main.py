from scraper import get_info, scrape_pages
from processor import get_relevance, get_related_comics
from nltk.corpus import wordnet
from database import reset_data

'''
comic = get_info(2276)

text = clean_text(comic.title.split())
print (text)
text = clean_text(comic.transcript.split())
print (text)
text = clean_text(comic.title_text.split())
print (text)
'''	

def query(word, comics, wordbank):
		pos = get_related_comics(word, wordbank)
		print (pos)
		cand = [[get_relevance(word, comics[comic_id]), comic_id] for comic_id in pos]
		cand = sorted(cand,reverse = True)
		return cand[0]


def main():
	#reset_data()
	
	comics, wordbank = scrape_pages()

	word = "coronavirus"

	w1 = wordnet.synset('safe.a.01')
	w2 = wordnet.synset('secure.a.01')
	print(w1.path_similarity(w2))

	print (query(word, comics, wordbank))
	


if __name__ == '__main__':
	main()

'''
Filter comics first by keywords, narrowing search pool (preliminary)
- use wordnet to get synonyms of queried key words, then match with words in the bank
- compare words in top N relevant comics to query words using spacy

Then, parse the filtered comics for exact matches (e.g. "Star Wars")
- Give high priority to exact matches of multiple search terms


'''