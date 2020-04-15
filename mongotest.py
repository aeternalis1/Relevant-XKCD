import pymongo

client = pymongo.MongoClient("mongodb+srv://m001-student:m001-mongodb-basics@sandbox-qtnas.mongodb.net/test?retryWrites=true&w=majority")

db = client["test"]
col = db["test"]

#col.insert_one({"_id": "test", "comics": [(10,2),(15,4),(5,3),(1,1)]})

word = "test"
cnt = 20
comic_num = 5

res = col.find({"_id": word})

for doc in res:
	comics = sorted(doc["comics"] + [[cnt, comic_num]], reverse = True)
	col.update_one({"_id": word}, {"$set": {"comics": comics}})