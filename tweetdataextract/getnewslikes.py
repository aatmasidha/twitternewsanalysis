import json
import logging
import logging.config
import os

import requests

logging.config.fileConfig( './configparam/logging.conf')
# create logger
logger = logging.getLogger('simpleExample')


# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.environ.get("BEARER_TOKEN")


def createURLForLikesForTweeterNews(newsId):
   # return "https://api.twitter.com/2/users/by?usernames={}&user.fields=created_at&expansions=pinned_tweet_id".format(userNames)
   return "https://api.twitter.com/2/tweets/{}/liking_users".format(newsId)

  	
def get_params():
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    return {"tweet.fields": "created_at", "user.fields" : "created_at,location"}


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
        logger.error("Error while processing url" + url)
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def getLikesForNewsTweetInformation(newsId):
    logger.debug("Inside def getLikesForNewsTweetInformation(newsId)")
    url = createURLForLikesForTweeterNews(newsId)
    params = get_params()
    json_response = connect_to_endpoint(url, params)
    logger.debug("Exit def getLikesForNewsTweetInformation(newsId)")
    return json_response

    
def main():
    newsID = "1528772793998970880"
    json_response = getLikesForNewsTweetInformation(newsID)
    print(json.dumps(json_response, indent=4, sort_keys=True))
    for record in json_response['data']:
         print(record)


if __name__ == "__main__":
    main()

