from models import Comic
from nltk.corpus import wordnet
import spacy

nlp = spacy.load('en_core_web_md') 

def relevance(word, words):
	res = [0]
	tokens = nlp(" ".join([word] + words))
	token1 = tokens[0]
	for i in range(1, len(tokens)):
		token2 = tokens[i]
		if token1.text == token2.text:
			res.append(1)
		elif not token1.is_oov and not token2.is_oov:
			try:
				cur = token1.similarity(token2)
				res.append(cur)
			except:
				pass
	res = sorted(res, reverse=True)
	num = min(10, len(res))
	return sum(res[:num]) / num


# (str, Comic) -> float
# gets relevance of comic to a word, represented as a float between 0-1
def get_relevance(word, comic):
	res = 20 * relevance(word, comic['title']) + 10 * relevance(word, comic['title_text'])
	res += 10 * relevance(word, comic['transcript']) + relevance(word, comic['explanation'])
	return res


# takes keyword, dictionaries of comics and wordbank
# returns list of comics
def get_related_comics(word, wordbank):
	cand = [word]	#candidate words

	try:
		for syn in wordnet.synsets(word):
			for l in syn.lemmas():
				cand.append(l.name())
	except:
		pass

	res = {}

	for word in set(cand):
		if word not in wordbank:
			continue
		for [occ, comic_id] in wordbank[word]:
			if comic_id in res:
				res[comic_id] += occ
			else:
				res[comic_id] = occ

	res = sorted([[res[comic_id], comic_id] for comic_id in res], reverse=True)

	return [x[1] for x in res][:min(len(res), 50)]