import json
import os
import logging
from logging import config

import requests
logging.config.fileConfig( './configparam/logging.conf')
# create logger
logger = logging.getLogger('simpleExample')


# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.environ.get("BEARER_TOKEN")

#Using this API we get the newsID and the headline for the news
#The number of news returned depends on max_results but if this parameter is
#not set we get 10 tweets by default per request

logging.config.fileConfig( './configparam/logging.conf')
# create logger
logger = logging.getLogger('simpleExample')


def createURLForTweeterNewsByUser(user_Name):
   userName = user_Name
   return "https://api.twitter.com/2/tweets/search/recent?query=from:{}&expansions=author_id&user.fields=created_at,location&max_results=20".format(userName)


def get_params():
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    #return {"tweet.fields": "created_at,geo"}
     return {"tweet.fields": "created_at,public_metrics"}



def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserTweetsPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)

    if response.status_code != 200:
        logger.error("Error while getting data from url:" + url)
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def getNewsTweetInformationByUser(twitterUserName):
    logger.debug("Inside def getNewsTweetInformationByUser(userNames)")
    url = createURLForTweeterNewsByUser(twitterUserName)
    params = get_params()
    json_response = connect_to_endpoint(url, params)
    logger.debug("Exit def getNewsTweetInformationByUser(userNames)")
    return json_response

    
def main():
    userName = "the_hindu"
    json_response = getNewsTweetInformationByUser(userName)
    print(json.dumps(json_response, indent=4, sort_keys=True))
    for record in json_response['data']:
         print(record['text'].encode('utf8'))


if __name__ == "__main__":
    main()

