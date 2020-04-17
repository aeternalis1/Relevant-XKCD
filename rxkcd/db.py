import pymongo
from .instance.config import MONGO_URI

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


def get_word_comics(word):
	col = db["wordbank"]
	try:
		cursor = col.find({"_id": word})
		for doc in cursor:
			return doc["comics"]
	except:
		return None
	return None