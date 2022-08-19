import pymongo
import pprint



myclient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myclient['twetteranalyse']
print("twetteranalyse:", mydb)
mycol = mydb["tweetsdata"]

# tweet_containing_corona = mycol.find({"NewsHeadLine" : {"$regex" : "tree{1}" }})
# printer.pprint(list(tweet_containing_corona))

#Here we are 

printer = pprint.PrettyPrinter()
# pprint.pprint(list(tweets_and_likes), indent=1)

# Here we are joing the collections  tweetsdata and likestweetsdata on the field

tweets_and_likes = mydb.tweetsdata.aggregate([{
    "$lookup" :{
                   "from" : "likestweetsdata",
                   "localField" : "LikeIds",
                   "foreignField" : "_id",
                   "as": "likeuser"
        }
    }])
printer.pprint(list(tweets_and_likes))


# tweets_and_likes = mydb.tweetsdata.aggregate([{
#     "$lookup" :{
#                    "from" : "likestweetsdata",
#                    "localField" : "LikeIds",
#                    "foreignField" : "_id",
#                    "as": "likeuser"
#         },
#         "$addFields" : {
#                   # "Max Response Time" : {"$max" : "Created At"} 
#                   "max": { "$max": "$Created At" }
#         }
#     }])
# printer.pprint(list(tweets_and_likes))
