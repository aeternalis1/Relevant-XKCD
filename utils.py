import string

# str -> str
# removes any formatting on ExplainXKCD
def remove_formatting(word):
	formats = ["<i>", "</i>", "<b>", "</b>", "<u>", "</u>"] # get rid of italicization, bold, etc
	for s in formats:
		word = word.replace(s,"")
	return word


# list -> list
# remove punctuation and capitalizations
def clean_text(word_list):
	table = str.maketrans('', '', string.punctuation)
	stripped = [(remove_formatting(w)).translate(table).lower() for w in word_list]
	return stripped