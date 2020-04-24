from nltk.corpus import wordnet
from .db import get_word_comics
from .utils import clean_text
import spacy
import math


def calc(a):	# function mapping [0,1] onto [0,1]
	return (math.sin(math.pi*(a-0.5))+1)/2

# ([str], [str]) -> float
# takes list of key words and reference text, returns comparison
def relevance(keywords, words, comic_num):	# pass in comic_num for debugging purposes
	return 1


# (str, Comic) -> float
# gets relevance of comic to a word, represented as a float between 0-1
def get_relevance(keywords, comic):
	return 1


# (str, Comic) -> integer
# gets number of exact matches of a sequence of keywords
def get_matches(keywords, comic):
	return 1


# ([str], dict()) -> [int]
# returns list of comic ids
def get_related_comics(keywords):
	return [x for x in range(1,20)]