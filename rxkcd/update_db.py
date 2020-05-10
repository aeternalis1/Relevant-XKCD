import pymongo
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from instance.config import MONGO_URI

client = pymongo.MongoClient(MONGO_URI)
db = client["xkcd"]

def insert_comic(comic):
	col = db["comics"]
	col2 = db["imgurls"]
	doc = {
		"_id": comic.id,
		"title": comic.title,
		"transcript": comic.transcript,
		"title_text": comic.title_text,
		"explanation": comic.explanation,
		"img_url": comic.img_url,
		"og_title": comic.og_title,
		"og_ttext": comic.og_ttext
	}
	try:
		col.insert_one(doc)
	except:
		print ("Error inserting comic %d in database." % comic.id)
	try:
		col2.insert_one({"_id": comic.id, "img_url": comic.img_url})
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
			if not comics or (comics[-1][0] > cnt and len(comics) < 20):
				comics = comics + [[cnt, comic.id]]
			else:
				for i in range(len(comics)):
					if cnt >= comics[i][0]:
						comics.insert(i, [cnt, comic.id])
						if len(comics) > 20:
							comics.pop(-1)
						col.update_one({"_id": word}, {"$set": {"comics": comics}})
						break


def update_wordbank_many(wordbank):		# resets wordbank 
	col = db["wordbank"]

	col.delete_many({})
	
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
						"explanation": comics[comic].explanation,
						"img_url": comics[comic].img_url
						})
	col.insert_many(to_insert)


def update_url(comic_num, url):
	col = db["comics"]
	col.update_one({"_id": comic_num}, {"$set": {"img_url": url}})
	col2 = db["imgurls"]
	col2.update_one({"_id": comic_num}, {"$set": {"img_url": url}})


def update_title(comic_num, title):
	col = db["comics"]
	col.update_one({"_id": comic_num}, {"$set": {"title": title}})


def update_og_title(comic_num, title):
	col = db["comics"]
	col.update_one({"_id": comic_num}, {"$set": {"og_title": title}})


def update_og_ttext(comic_num, ttext):
	col = db["comics"]
	col.update_one({"_id": comic_num}, {"$set": {"og_ttext": ttext}})


# temporary function: cut entries in wordbank down to 20 comics
def trim_db():
	col = db["wordbank"]
	for doc in col.find():
		comics = doc["comics"]
		if len(comics) > 20:
			col.update_one({"_id": doc["_id"]}, {"$set": {"comics": comics[:20]}})


def exists(path):
    r = requests.head(path)
    print (r.status_code)
    return r.status_code == requests.codes.ok


# temporary function: add new collection for only image urls, for quicker access
def add_url_col():
	col = db["comics"]
	col2 = db["imgurls"]
	for comic in col.find():
		if 'img_url' in comic and exists(comic['img_url']):
			col2.insert_one({"_id": comic['_id'], "img_url": comic['img_url']})


if __name__ == "__main__":
	add_url_col()