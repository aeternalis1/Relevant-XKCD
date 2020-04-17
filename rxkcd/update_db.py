import pymongo
from .instance.config import MONGO_URI

client = pymongo.MongoClient(MONGO_URI)
db = client["xkcd"]

def insert_comic(comic):
	col = db["comics"]
	doc = {
		"_id": comic.id,
		"title": comic.title,
		"transcript": comic.transcript,
		"title_text": comic.title_text,
		"explanation": comic.explanation,
	}
	try:
		col.insert_one(doc)
	except:
		print ("Error inserting comic %d in database." % comic.id)


def update_wordbank_one(comic):		# updates wordbank with single new comic
	col = db["wordbank"]
	words = {}
	for word in comic.title + comic.transcript + comic.title_text + comic.explanation:
		if word in words:
			words[word] += 1
		else:
			words[word] = 1
	for word in words:
		cnt = words[word]
		try:
			cursor = col.find({"_id": word})
		except:
			col.insert_one({"_id": word, "comics": [[cnt, comic.id]]})
			continue
		for doc in cursor:
			comics = doc["comics"]	# already sorted in reverse order (by assumption)
			if not comics or comics[-1][0] > cnt:
				comics = comics + [[cnt, comic.id]]
			else:
				for i in range(len(comics)):
					if cnt >= comics[i][0]:
						comics.insert(i, [cnt, comic.id])
						break
			try:
				col.update_one({"_id": word}, {"$set": {"comics": comics}})
			except:
				print ("Error updating word %s, comic %d." % (word, comic.id))
				continue


def update_wordbank_many(wordbank):		# updates given list of words
	col = db["wordbank"]

	col.delete_many({"_id": {"$in": list(wordbank.keys())}})

	to_insert = []
	for word in wordbank:
		comics = wordbank[word]
		to_insert.append({"_id": word, "comics": comics})
	col.insert_many(to_insert)


def update_comics_many(comics):		# updates list of comics
	col = db["comics"]

	col.delete_many({"_id": {"$in": [comics[comic].id for comic in comics]}})

	to_insert = []
	for comic in comics:
		to_insert.append({
						"_id" : comics[comic].id,
						"title": comics[comic].title,
						"title_text": comics[comic].title_text,
						"transcript": comics[comic].transcript,
						"explanation": comics[comic].explanation
						})
	col.insert_many(to_insert)