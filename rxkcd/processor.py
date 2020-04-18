from nltk.corpus import wordnet
from .db import get_word_comics
import spacy
import math

nlp = spacy.load('en_core_web_md') 

# ([str], [str]) -> float
# takes list of key words and reference text, returns comparison
def relevance(keywords, words):
	tokens = nlp(" ".join(keywords + words))
	weight = [[0] for x in range(len(keywords))]
	keys = [tokens[x] for x in range(len(keywords))]
	for i in range(len(keywords), len(tokens)):
		token2 = tokens[i]
		for j in range(len(keys)):
			token = keys[j]
			if token.text == token2.text:
				weight[j].append(1)
			elif token.has_vector and token2.has_vector:
				cur = token.similarity(token2)
				weight[j].append(cur)
	res = 1
	for i in range(len(keys)):
		weight[i] = sorted(weight[i],reverse=True)
		num = min(15, 2*int(math.sqrt(len(words)))+1)
		res *= (sum(weight[i][:num]) / num)
	return res


# (str, Comic) -> float
# gets relevance of comic to a word, represented as a float between 0-1
def get_relevance(keywords, comic):
	res = 0.4 * (relevance(keywords, comic['title_text']) + relevance(keywords, comic['transcript']))
	res += 0.2 * relevance(keywords, comic['explanation'])
	if res:
		res *= min(relevance(keywords, comic['title']) + 1, 1/res)
	else:
		res = relevance(keywords, comic['title'])
	return res


# ([str], dict()) -> [int]
# returns list of comic ids
def get_related_comics(keywords):
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
			comics = get_word_comics(word)
			if not comics:
				continue
			for [occ, comic_id] in comics:
				if comic_id in res:
					res[comic_id] += occ
				else:
					res[comic_id] = occ

	res = sorted([[res[comic_id], comic_id] for comic_id in res], reverse=True)

	return [x[1] for x in res][:min(20,len(res))]