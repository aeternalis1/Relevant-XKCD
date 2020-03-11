from models import Comic
from nltk.corpus import wordnet
import spacy

nlp = spacy.load('en_core_web_md') 

# ([str], [str]) -> float
# takes list of key words and reference text, returns comparison
def relevance(keywords, words):
	res = [0]
	tokens = nlp(" ".join(keywords + words))
	keys = [tokens[x] for x in range(len(keywords))]
	for i in range(len(keywords), len(tokens)):
		token2 = tokens[i]
		for token in keys:
			if token.text == token2.text:
				res.append(1)
			elif token.has_vector and token2.has_vector:
				cur = token.similarity(token2)
				res.append(cur)
	res = sorted(res, reverse=True)
	num = min(10, len(res))
	return sum(res[:num]) / num


# (str, Comic) -> float
# gets relevance of comic to a word, represented as a float between 0-1
def get_relevance(keywords, comic):
	res = 20 * relevance(keywords, comic['title']) + 10 * relevance(keywords, comic['title_text'])
	res += 10 * relevance(keywords, comic['transcript']) + relevance(keywords, comic['explanation'])
	return res


# ([str], dict()) -> [int]
# returns list of comic ids
def get_related_comics(keywords, wordbank):
	res = {}
	for word in keywords:
		cand = [word]	#candidate words

		try:
			for syn in wordnet.synsets(word):
				for l in syn.lemmas():
					cand.append(l.name())
		except:
			pass

		for word in set(cand):
			if word not in wordbank:
				continue
			for [occ, comic_id] in wordbank[word]:
				if comic_id in res:
					res[comic_id] += occ
				else:
					res[comic_id] = occ

	res = sorted([[res[comic_id], comic_id] for comic_id in res], reverse=True)

	return [x[1] for x in res][:min(len(res), 20)]