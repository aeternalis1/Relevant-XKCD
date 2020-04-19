from nltk.corpus import wordnet
from .db import get_word_comics
import spacy
import math

nlp = spacy.load('en_core_web_md') 


def calc(a):	# function mapping [0,1] onto [0,1]
	return (math.sin(math.pi*(a-0.5))+1)/2

# ([str], [str]) -> float
# takes list of key words and reference text, returns comparison
def relevance(keywords, words, comic_num):
	lst = keywords+words
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
				cur = calc(token.similarity(token2))
				weight[j].append(cur)

	match = 2
	i = 0
	while i < len(words):		# add heuristic for exact match
		j = 0
		while i+j < len(words) and j < len(keywords) and words[i] == keywords[j]:
			j += 1
		if j == len(keywords):
			match += 1
		i += j+1

	for i in range(len(weight)):
		weight[i] = sorted(weight[i], reverse=True)
		num = min(10, 2*int(math.sqrt(len(weight[i])))+1)
		weight[i] = sum(weight[i][:num]) / num

	res = (sum(weight)/len(weight)) * min(weight)

	num = min(5, int(math.sqrt(len(words)))+1)
	res = min(1, res * math.log(match,2))

	return res


# (str, Comic) -> float
# gets relevance of comic to a word, represented as a float between 0-1
def get_relevance(keywords, comic):
	res = 0.4 * relevance(keywords, comic['title_text'] + comic['transcript'], comic['_id'])
	res += 0.2 * relevance(keywords, comic['explanation'], comic['_id'])
	if res:
		res *= min(relevance(keywords, comic['title'], comic['_id']) + 1, 1/res)
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