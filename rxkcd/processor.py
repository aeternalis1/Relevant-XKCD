from nltk.corpus import wordnet
from db import get_word_comics
from utils import clean_text
import spacy
import math

nlp = spacy.load('en_core_web_md') 


def calc(a):	# function mapping [0,1] onto [0,1]
	return (math.sin(math.pi*(a-0.5))+1)/2

# ([str], [str]) -> float
# takes list of key words and reference text, returns comparison
def relevance(keywords, words, comic_num):	# pass in comic_num for debugging purposes
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

	for i in range(len(weight)):
		weight[i] = sorted(weight[i], reverse=True)
		num = min(15, int(len(weight[i])/2)+1, len(weight[i]))
		if not num:
			continue
		weight[i] = sum(weight[i][:num]) / num

	res = (sum(weight)/len(weight)) * min(weight)

	return res


# (str, Comic) -> float
# gets relevance of comic to a word, represented as a float between 0-1
def get_relevance(keywords, comic):
	res = 0.5 * relevance(keywords, comic['title_text'] + comic['transcript'], comic['_id'])
	res += 0.3 * relevance(keywords, comic['explanation'], comic['_id'])
	tmp = relevance(keywords, comic['title'], comic['_id'])
	if res:
		res = max(res, res*(tmp+0.8))
	else:
		res = tmp
	res = max(res, math.sqrt(tmp))
	return min(1,res)


# (str, Comic) -> integer
# gets number of exact matches of a sequence of keywords
def get_matches(keywords, comic):
	words = comic['title_text'] + comic['transcript'] + comic['explanation'] + comic['title']
	i = 0
	matches = 0
	while i < len(words):		# add heuristic for exact match
		j = 0
		while i+j < len(words) and j < len(keywords) and words[i+j] == keywords[j]:
			j += 1
		if j == len(keywords):
			matches += 1
		i += j+1
	return matches


# ([str], dict()) -> [int]
# returns list of comic ids
def get_related_comics(keywords):
	res = {}
	cnt = {}
	for keyword in keywords:
		tmp = {}
		synonyms = [keyword]	#candidate words
		try:
			for syn in wordnet.synsets(keyword):
				for l in syn.lemmas():
					synonyms.append("".join(clean_text(l.name().split('_'))))
		except:
			pass
		cand = []
		for word in synonyms:
			if word not in cand:
				cand.append(word)
		tokens = nlp(" ".join(cand))
		for i in range(len(cand)):
			word = cand[i]
			comics = get_word_comics(word)
			if not comics:
				continue
			tot = sum([comic[0] for comic in comics])
			mul = 1
			if word == keyword:
				mul = 1
			elif tokens[0].has_vector and tokens[i].has_vector:
				mul = calc(tokens[0].similarity(tokens[i]))
			else:
				mul = 0.5	# ehhhh suboptimal but unavoidable

			for [occ, comic_id] in comics:
				if comic_id in tmp:
					tmp[comic_id] += (occ/tot)*mul
				else:
					tmp[comic_id] = (occ/tot)*mul

		for comic_id in tmp:
			if comic_id in res:
				res[comic_id] = (res[comic_id]*cnt[comic_id]+tmp[comic_id])/(cnt[comic_id]+1)
				cnt[comic_id] += 1
			else:
				res[comic_id] = tmp[comic_id]
				cnt[comic_id] = 1

	for comic_id in res:
		res[comic_id] = (res[comic_id]*cnt[comic_id])/len(keywords)

	res = sorted([[res[comic_id], comic_id] for comic_id in res], reverse=True)

	return [x[1] for x in res][:min(30,len(res))]