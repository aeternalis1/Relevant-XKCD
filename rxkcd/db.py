import pymongo

from instance.config import MONGO_URI
from update_db import insert_comic, update_wordbank_one, exists
from scraper import get_info

client = pymongo.MongoClient(MONGO_URI)
db = client["xkcd"]


def get_comic(comic_num):
	col = db["comics"]
	try:
		cursor = col.find({"_id": comic_num})
		for doc in cursor:
			return doc
	except:
		print ("Error fetching comic %d in database." % comic.id)
	return None


def get_img_url(comic_num):
	col = db["imgurls"]
	try:
		cursor = col.find({"_id": comic_num})
		for doc in cursor:
			return doc
	except:
		print ("Error fetching comic %d in database." % comic.id)
	return None


def get_word_comics(word):
	col = db["wordbank"]
	try:
		cursor = col.find({"_id": word})
		for doc in cursor:
			return doc["comics"]
	except:
		return None
	return None


def get_recent():
	col = db["comics"]
	for doc in col.find({"_id": "latest_comic"}):
		latest_num = doc["num"]
		recent = []
		for j in range(latest_num+1, latest_num+10):
			if exists("https://xkcd.com/%d/" % j):
				recent.append(j)
		if len(recent) > 5:		# want to give some buffer time to allow explainXKCD to update
			comic = get_info(recent[0])
			insert_comic(comic)
			update_wordbank_one(comic)
			col.update_one({"_id": "latest_comic"}, {"$set": {"num": recent[0]}})