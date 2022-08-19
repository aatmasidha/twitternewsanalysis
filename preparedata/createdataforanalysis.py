from _queue import Empty
from datetime import datetime
import json
import logging
import os
import re

from bs4 import BeautifulSoup
from fontTools.feaLib import location
from jproperties import Properties
import nltk
from nltk.corpus import subjectivity
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests

import configparam.constants as constants
import configparam.readconfigparam as readConfig
import utils.ProcessText as ProcessText


# import bbcnews
nltk.download('omw-1.4')

logging.config.fileConfig( './configparam/logging.conf')
# create logger
logger = logging.getLogger('simpleExample')

# logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

configs = Properties()

def findSensitivityAndPolarity(urlList, tagToParse):

    values = {}
    # url = "https://www.bbc.co.uk/news/uk-61681066"
    
    # Sometimes there are multiple news URLs associated with the news we will consolidate all the news as one content 
    # to understand the sensitivity of the news
    for url in urlList:
       
        logger.debug("Getting news details from URL:" + url)
        res = requests.get(url)
        html_page = res.content    
        
        soup = BeautifulSoup(html_page, 'html.parser')
        text = soup.get_text()
        articleString = ''
        
        # The contents are present inside the article tag in the HTML. This is general observation for 
        # most of the news papers
        # for content in soup.find_all("article"):
        for content in soup.find_all(tagToParse):
            articleString = articleString + content.text
            articleString = articleString.strip("\n")
        
        # We remove some characters from the content like @
        articleString = ProcessText.clean_tweet(articleString)
                
        # allwords = ' '.join(articleString)
        # wordCloud = WordCloud(width = 500, height = 30, random_state = 21, max_font_size = 119).generate(allwords)
        # plt.imshow(wordCloud, interpolation = "bilinear")
        # plt.axis("off")
        # plt.show()
        
        sid = SentimentIntensityAnalyzer()
        values['articleText'] = articleString
        scores = sid.polarity_scores(articleString)
        values['score'] = scores

        # article = values.get('articleText')

        return values


def readFilesFromDailyPath():
    jsonPath = '.'
    logger.info('readJSONFile')
    configParam = readConfig.readConfigurationFile()
    jsonPath = configParam[constants.JASON_PATH]
    
    jsonFiles = os.listdir(jsonPath)
 
    print("Files and directories in '", jsonPath, "' :")
 
    # prints all files
    print(jsonPath)
    validFileList = []
    for file in jsonFiles:
        match = re.search("\.json$", file)
        if match:
            print("The file ending with .json is:", file)
            validFileList.append(file)
         
    if(len(validFileList)):
        for file in validFileList:
            # readJSONFile( jsonFolder + "/" + file)
            readJSONFileByItems(jsonPath + "/" + file)
            

def processReTweetNewsInformation(retweetInData):
    retweetIDArray = []
    retweetuserinfo = []
    for reTweetKey, reTweetValue in retweetInData.items():
        userNameR = retweetID = userLocation = name = createdDate = ''
        for reTweetValueKey, reTweetValueValue in reTweetValue.items():
            if reTweetValueKey == 'reUserName':
                userNameR = ProcessText.clean_tweet(reTweetValueValue)
            if reTweetValueKey == 'retweetID': 
                retweetID = reTweetValueValue
                retweetIDArray.append(retweetID)
            if reTweetValueKey == 'reTweetLocation': 
                userLocation = ProcessText.clean_tweet(reTweetValueValue)
            if reTweetValueKey == 'reTweetName': 
                name = ProcessText.clean_tweet(reTweetValueValue)
            if reTweetValueKey == 'created_at': 
                createdDate = reTweetValueValue
        if(len(retweetID) > 0):
            retweetuserinfo.append({"ID" : retweetID, "name" : name, "userName" : userNameR, "location" : userLocation,"created_at":createdDate})
    
    return retweetuserinfo, retweetIDArray                                    

def processLikeNewsInformation(likeInData):
    likeIDArray = []
    likesInfo = []         
    for likesKey, likesValue in likeInData.items():
        userNameR = likeID = userLocation = name = createdDate = ''
        for likesValueKey, likesValueValue in likesValue.items():
            if likesValueKey == 'likesUserName':
                userNameR = ProcessText.clean_tweet(likesValueValue)
            if likesValueKey == 'likesID': 
                likeID = likesValueValue
                likeIDArray.append(likeID)
            if likesValueKey == 'Location': 
                userLocation = ProcessText.clean_tweet(likesValueValue)
            if likesValueKey == 'LikesName': 
                name = ProcessText.clean_tweet(likesValueValue)
            if likesValueKey == 'created_at': 
                createdDate = likesValueValue
        if(len(likeID) > 0):                
            likesInfo.append({"ID" : likeID, "name" : name, "userName" : userNameR, "location" : userLocation, "created_at":createdDate})
    return likesInfo, likeIDArray

def readJSONFileByItems(fileName):
    try:
        # Read the json file by news handler
        with open(fileName) as json_file:
            data = json.load(json_file)
            
            # Read news agency details from the json file
            for newAgencyKey, newsAgencyvalue in data.items():
                newsAgencyName = ''
                captureDate = ''
                newsDetailsValue = newsAgencyvalue['newsAccountDetails']
                newsAgencyName = newsDetailsValue['newsaccounthandler']
                captureDate = newsDetailsValue['capturedate']
                jsonString = ''
                jsonDump = []
                             
                cnt = 0
                # Read one by one news details                   
                for newsDetailsKey in newsAgencyvalue:
                    newsDetailsValue = newsAgencyvalue[newsDetailsKey]
                    print(newAgencyKey, newsDetailsKey)
                    if('newsId_' in  newsDetailsKey):
                        newsId = ''
                        text = ''
                        retweetCount = 0
                        likesCount = 0
                        commentCount = 0
                        positiveCommentCnt = 0 
                        negativeCommentCnt = 0
                        neutralCommentCnt = 0
                        retweetuserinfo = []
                        retweetIDArray = []
                        likesInfo = []
                        commentInfo = []
                        likeIDArray = []
                        commentIDArray = []
                        record = {}
                        for newsKey, newsValue in newsDetailsValue.items():
                            if newsKey == 'id':
                                newsId = newsValue
                                record['newsId'] = newsId
                            elif newsKey == 'text':
                                orgText = newsValue
                                text = ProcessText.clean_tweet(newsValue)
                                if(len(str(text)) == 0):
                                    print("text is empty")
                                
                                # custom_tweet = "smartwatch market india has witnessed tremendous growth with companies offering wide variety smartwatches this review we will talk about its latest launch noise colorfit pro 4 writes"
                                record['text'] = text
                                urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', orgText)
                                print("Original string: ", text)
                                
                                if(urls != None and  len(urls) > 0):
                                    print("Urls: ", urls)
                                    # newAgencyName =      
                                    tagToParse = 'article'
                                    if(newsAgencyName == 'AJEnglish'):
                                        tagToParse = 'p'
                                    newsDetailsAndSensitivity = findSensitivityAndPolarity(urls, tagToParse)
                                    record['articleText'] = newsDetailsAndSensitivity['articleText']
                                else:
                                    values = {}
                                    articleString = text
                                    sid = SentimentIntensityAnalyzer()
                                    values['articleText'] = articleString
                                    scores = sid.polarity_scores(articleString)
                                    values['score'] = scores
                            
                                    article = text                                    
                                    # Initializing the sentiment analyser
                                    logger.debug("Start - Processing the sensitivity by ProcessText....")
                                    logger.debug("Article Contents are:" + article)
                                    record['articleText'] = articleString 
                            elif newsKey == 'summary':
                                record['reTweetCount'] = newsValue['retweet_count']
                                record['likesCount'] = newsValue['like_count']
                                record['commentCount'] = newsValue['reply_count']
                                record['retweetIDs'] = retweetIDArray
                                record['likeIds'] = likeIDArray
                                record['commentIds'] = commentIDArray
    
                            elif newsKey == 'newsRetweetDict':
                                reTweetRecords = newsValue
                                retweetuserinfo, retweetIDArray = processReTweetNewsInformation(newsValue)        
                                    # reTweetTagValue = ProcessText.clean_tweet(reTweetValue)
                                
                                if 'reTweetCount' not in record.keys():
                                    retweetCount = len(newsValue)
                                    record['reTweetCount'] = retweetCount 
                                else:
                                    retweetCount  = record['reTweetCount']
                                    
                                record['retweetuserinfo'] = retweetuserinfo
                                record['retweetIDs'] = retweetIDArray
                            elif  newsKey == 'newsLikesDict':
                                likesRecord = newsValue
                                
                                # likeIDArray = []
                                likesInfo, likeIDArray = processLikeNewsInformation(newsValue)    
                                
                                if 'likesCount' not in record.keys():        
                                    likesCount = len(likesRecord)
                                    record['likesCount'] = likesCount
                                else:
                                    likesCount = record['likesCount']
                                record['likeIds'] = likeIDArray
                                record['likesuserinfo'] = likesInfo
                                
                                # TO DO to get the list of locations
                                # get the list in set so we will get locations only once
                            elif newsKey == 'newsCommentDict':
                                
                                for commentKey, commentValue in newsValue.items():
                                    commentUserID = commentID = comment = location = createdDate = ''
                                    for commentTagKey, commentTagValue in commentValue.items():
                                        if commentTagKey == 'commentText':
                                            # commentTagValue = ProcessText.cleanText(commentTagValue)
                                            commentTagValue = ProcessText.clean_tweet(commentTagValue)
                                            comment = commentTagValue
                                        if commentTagKey == 'commentID':
                                            commentID = commentTagValue
                                            commentIDArray.append(commentID)
                                        if commentTagKey == 'commentUserID':
                                            commentUserID = commentTagValue
                                        if commentTagKey == 'location':
                                            location = commentTagValue
                                        if commentTagKey == 'created_at': 
                                            createdDate = commentTagValue
                                    commentInfo.append({"commentUserID":commentUserID,"commentID": commentID,"commentText" :comment, "location": location,"created_at":createdDate} )
                                commentRecord = newsValue   
                                commentCount = len(commentRecord)
                                if 'commentCount' not in record.keys():
                                    record['commentCount'] = commentCount
                                else:
                                    commentCount = record['commentCount']  
                                record['commentInfo'] = commentInfo
                                
                                record['positvecommentcount'] = positiveCommentCnt
                                record['negativecommentcount'] = negativeCommentCnt
                                record['neutralcommentcount'] = neutralCommentCnt

                            elif newsKey == 'created_at':
                                record['created_at'] = newsValue         
    
                        record['reTweetCount'] = retweetCount        
                        record['retweetIDs'] = retweetIDArray
                        record['likesCount'] = likesCount
                        record['likeIds'] = likeIDArray
                        record['commentCount'] = commentCount
                        record['commentIds'] = commentIDArray
                                # TO DO to remove the comma and other characters from the location
                                # record['location'] = commentValue['location']
                            
                        # jsonDump[newsId] = record
                        record['newshandler'] = newsAgencyName    
                        record['capturedate'] = captureDate
                        jsonDump.append(record)
                        cnt = cnt + 1
                # jsonDump[cnt] = record                        
        # executionDateTime = datetime.now()
        match = re.search(r'\d{4}_\d{2}_\d{2}_T_\d{2}_\d{2}_\d{2}', fileName)
        date = datetime.strptime(match.group(), '%Y_%m_%d_T_%H_%M_%S')
        # date.replace(" ","T")
        date_time = date.strftime("%Y_%m_%d_T_%H_%M_%S")
        print("date and time:",date_time)    
        print(date_time)
        
        # outputIndex = fileName.find('_output_', 0)
        # username = fileName[0:outputIndex]
        # timeStr = executionDateTime.strftime("%H_%M_%S")        
        # dateStr = (executionDateTime).strftime("%Y_%m_%d")    
        configParam = readConfig.readConfigurationFile()
        outputPath = configParam['outputpath']
    
        
        with open( outputPath + "/" + newsAgencyName + "_" +"output" + "_" + date_time+ ".json", 'w', encoding='utf8') as json_file:
            json.dump(jsonDump, json_file, indent=4)
        

    except json.decoder.JSONDecodeError as jsonErr:
            logger.error("Could not parse the file:" + fileName)
            logger.error(f"Unexpected {jsonErr=}, {type(jsonErr)=}")
            
    except BaseException as err:
            logger.error(f"Unexpected {err=}, {type(err)=}")
        
def main(): 
    logger.info('Started')
    readFilesFromDailyPath()
    
    
if __name__ == '__main__':
    main()
