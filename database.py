import json
from scraper import scrape_pages


# scrapes comics again and resets data
def reset_data():
	comics, wordbank = scrape_pages()

	wordbank_file = open('wordbank.txt', 'w')
	json.dump(wordbank, wordbank_file)

	comics_file = open('comics.txt', 'w')
	for comic in comics:
		comics[comic] = {
							"id" : comics[comic].id,
							"title": comics[comic].title,
							"title_text": comics[comic].title_text,
							"transcript": comics[comic].transcript,
							"explanation": comics[comic].explanation
						}
	json.dump(comics, comics_file)


# gets comics, wordbank
def retrieve_data():
	pass


# updates data with new comic
def new_comic():
	pass


'''
Alas, usage of relational databases is restricted in Waterloo Residences

So for now I'll just use files

'''