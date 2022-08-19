from pymongo import MongoClient
import pprint
# Requires the PyMongo package.
# https://api.mongodb.com/python/current

client = MongoClient('mongodb://localhost:27017/')
result = client['twitteremotiondb']['tweetsdata'].aggregate([
    {
        '$project': {
            '_id': 1, 
            'NewsHandler': 1, 
            'CreatedAt': 1, 
            'NewsCategory': 1, 
            'BertEmotion': 1, 
            'NumReTweets': 1,
            'Text2Emotion' : 1, 
            'NumLikes': 1, 
            'NumComments': 1
        }
    }, 
    {
        '$lookup': {
            'from': 'commenttweetsdata', 
            'localField': '_id', 
            'foreignField': 'NewsRef', 
            'as': 'commentdata'
        }
    },
   


    
    # {
    #     '$group': {
    #         '_id': {
    #             'source': '$NewsHandler', 
    #             'CreatedAt': '$CreatedAt'
    #         }, 
    #         'numComments': {
    #             '$sum': {
    #                 '$toInt': '$NumComments'
    #             }
    #         }, 
    #         'numRetweets': {
    #             '$sum': {
    #                 '$toInt': '$NumReTweets'
    #             }
    #         }   
    #     }
    # }, {
    #     '$sort': {
    #         'count': -1
    #     }
    # }
])

printer = pprint.PrettyPrinter()
printer.pprint(list(result))


