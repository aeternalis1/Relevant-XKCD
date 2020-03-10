from models import Comic
from nltk.corpus import wordnet
import spacy

nlp = spacy.load('en_core_web_md') 

def relevance(word, words):
	res = [0]
	for w in words:
		if w == word:
			res.append(1)
		else:
			try:
				tokens = nlp(word + " " + w)
				res.append(tokens[0].similarity(tokens[1]))
			except:
				pass
	res = sorted(res, reverse=True)
	num = min(10, len(res))
	return sum(res[:num]) / num


# (str, Comic) -> float
# gets relevance of comic to a word, represented as a float between 0-1
def get_relevance(word, comic):
	w1 = word+".n.01"
	res = 20 * relevance(word, comic.title) + 10 * relevance(word, comic.title_text)
	res += 10 * relevance(word, comic.transcript) + relevance(word, comic.explanation)
	print (res,comic.id)
	return res


# takes keyword, dictionaries of comics and wordbank
# returns list of comics
def get_related_comics(word, wordbank):
	cand = [word]	#candidate words
	for syn in wordnet.synsets(word):
		for l in syn.lemmas():
			cand.append(l.name())

	res = []

	for word in set(cand):
		if word not in wordbank:
			continue
		for [occ, comic_id] in wordbank[word]:
			res.append(comic_id)

	return res