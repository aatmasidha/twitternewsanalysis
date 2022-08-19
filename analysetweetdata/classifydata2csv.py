from _queue import Empty
from datetime import datetime
import json
import logging
import os
import re

from jproperties import Properties
import nltk
from nltk.corpus import subjectivity
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests
from transformers import pipeline

import configparam.constants as constants
import configparam.readconfigparam as readConfig
from model.naivebayesclassifer import bbcnews
import text2emotion as te
from utils import ProcessText
import csv
# import bbcnews
nltk.download('omw-1.4')

logger = logging.getLogger(__name__)
# logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

configs = Properties()


def getAnalysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'  


def emotion_detection_text2emotion(x):
    try:
        all_emotions_value = te.get_emotion(x)
        Keymax_value = max(zip(all_emotions_value.values(), all_emotions_value.keys()))[1]
        return Keymax_value
    except BaseException as err:
            logger.error(f"Unexpected {err=}, {type(err)=}")

def readOutputJSONFile(outputJsonFile):
    logger.debug("readOutputJSONFile")
    try:
        newsAnalysisArray = []
        # newsResponseArray = []
        likesResponseArray = []
        reTweetResponseArray = []
        commentResponseArray = []   #0     1,             2,                3,              4,             5,              6               7              8            9          10         11                12          13            14
        newsAnalysisHeading = ['NewsID', 'NewsHeadLine', 'NewsSensitivity','NewsCategory', 'NewsPolarity','BertEmotion', 'Text2Emotion' , 'NumReTweets', 'RetweetIds', 'NumLikes', 'LikeIds', 'NumComments', 'CommentIDs','CreatedAt','NewsHandler']
        likesResponseHeading = ['UserID', 'LikesUserName', 'Location', 'CreatedAt','NewsRef']
        reTweetResponseArrayHeading = ['UserID', 'ReTweetUserName', 'Location', 'CreatedAt','NewsRef']
        commentResponseArrayHeading = ['UserID', 'Comment','Emotion','CommentUserName', 'Location', 'CreatedAt','NewsRef']

        fileObject = open(outputJsonFile, "r")
        jsonContent = fileObject.read()
        aList = json.loads(jsonContent)
        
        for item in aList:
            array = [] 
            newsID = ''
            created_at = ""
            newsHandler = ""
            text = ''
            for keyData, valueData in item.items():
                if(keyData == "newsId"):
                    newsID = valueData
                    array.insert(0, valueData)
                if(keyData == "text"):
                    text = valueData
                    array.insert(1, text)
                    
                    subjectivity = ProcessText.getSubjectivity(text)
                    array.insert(2, subjectivity)

                    classifier = bbcnews.classifier(text)
                    array.insert(3, classifier)                    

                    if(len(str(text)) != 0):
                        newsPolarity=  getAnalysis(ProcessText.getPolarity(text))  
                        # processMap['package_headline'] = emotion_value
                        array.insert(4, newsPolarity)
                        
                        model_id = "aatmasidha/distilbert-base-uncased-finetuned-emotion"
                        bertClassifier = pipeline("text-classification", model=model_id)
                        preds = bertClassifier(text, return_all_scores=False)
                        print(preds)
                        maxScore = -2 
                        maxEmotion = ''
                        for eval in preds:
                            emotion = eval.get('label')
                            predScore = eval.get('score')
                            if( predScore >  maxScore):
                                maxScore = predScore
                                maxEmotion = emotion
                            
                        array.insert(5,maxEmotion)
                        
                        # processMap['bert_headline'] = preds
                        
                        
                    else:
                        # processMap['bert_headline'] = 'NA'
                        # processMap['package_headline'] = 'NA'
                        array.insert(4, 'NA')
                        array.insert(5, 'NA')   

                if( keyData == 'articleText'):
                        emotion_value = emotion_detection_text2emotion(valueData)
                        # processMap['package_headline'] = emotion_value
                        array.insert(6, emotion_value)    

                    
                if(keyData == 'reTweetCount'):    
                    array.insert(7, valueData)
                    print( array)
                elif(keyData == 'retweetIDs'):
                    array.insert(8, valueData)
                    
                elif(keyData == 'likesCount'):
                    array.insert(9, valueData)  
                elif(keyData == 'likeIds'):
                    array.insert(10, valueData)
                
                elif(keyData == 'commentCount'):
                    array.insert(11, valueData)  
                elif(keyData == 'commentIds'):
                    array.insert(12, valueData)    
                    
                elif(keyData == 'created_at'):
                    # array.insert(13, valueData)
                    created_at = valueData    
                elif(keyData == 'newshandler'):
                    newsHandler = valueData
                elif(keyData == 'likesuserinfo'):
                    likesDataList= valueData
                    for likesInfo in likesDataList:
                        arrayLikes = []
                        arrayLikes.insert(0, likesInfo.get("ID"))
                        arrayLikes.insert(1, likesInfo.get("userName"))
                        arrayLikes.insert(2, likesInfo.get("location"))
                        arrayLikes.insert(3, likesInfo.get("created_at"))
                        arrayLikes.insert(4, newsID)
                        likesResponseArray.append(arrayLikes) 
                elif(keyData == "retweetuserinfo"):
                    reTweetDataList= valueData
                    for reTweetInfo in reTweetDataList:
                        arrayReTweet = []
                        arrayReTweet.insert(0, reTweetInfo.get("ID"))
                        arrayReTweet.insert(1, reTweetInfo.get("userName"))
                        arrayReTweet.insert(2, reTweetInfo.get("location"))
                        arrayReTweet.insert(3, reTweetInfo.get("created_at"))
                        arrayReTweet.insert(4, newsID)
                        reTweetResponseArray.append(arrayReTweet) 
                # NewsID', 'Comment','Emotion','CommentUserName', 'Location        
                elif(keyData == "commentInfo"):
                    commentList= valueData
                    for commentInfo in commentList:
                        comment = []
                        comment.insert(0, commentInfo.get("commentID"))
                        
                        commentText = commentInfo.get("commentText")
                        comment.insert(1, commentText)
                        
                        model_id = "aatmasidha/distilbert-base-uncased-finetuned-emotion"
                        bertClassifier = pipeline("text-classification", model=model_id)
                        preds = bertClassifier(comment, return_all_scores=False)
                        print(preds)
                        maxScore = -2 
                        maxEmotion = ''
                        for cnt in range(len(preds)):
                            eval = preds[cnt]
                            emotion = eval.get('label')
                            predScore = eval.get('score')
                            if( predScore >  maxScore):
                                maxScore = predScore
                                maxEmotion = emotion
                        comment.insert(2, maxEmotion)
                        comment.insert(3, commentInfo.get("commentUserID"))
                        comment.insert(4, commentInfo.get("location"))
                        comment.insert(5, likesInfo.get("created_at"))
                        comment.insert(6, newsID)
                        commentResponseArray.append(comment)
                # else:
                #     processMap[keyData] = valueData
            array.insert(13, created_at)
            array.insert(14, newsHandler)
            newsAnalysisArray.append(array)
        # executionDateTime = datetime.now()
        # timeStr = executionDateTime.strftime("%H_%M_%S")        
        # dateStr = (executionDateTime).strftime("%Y_%m_%d")
        
        match = re.search(r'\d{4}_\d{2}_\d{2}_T_\d{2}_\d{2}_\d{2}', outputJsonFile)
        date = datetime.strptime(match.group(), '%Y_%m_%d_T_%H_%M_%S')
        # date.replace(" ","T")
        date_time = date.strftime("%Y_%m_%d_T_%H_%M_%S")
        print("date and time:",date_time)    
        print(date_time)
        
        outputIndex = outputJsonFile.find('_output_', 0)
        username = outputJsonFile[0:outputIndex]

        fName =  username + "" + "_analysis_" + date_time + ".csv"
        with open(fName, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
                
            # writing the fields 
            csvwriter.writerow(newsAnalysisHeading) 
                
            # writing the data rows 
            csvwriter.writerows(newsAnalysisArray)
        
        fName =  username + "" + "_likes_analysis_" + date_time + ".csv"    
        with open(fName, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
                
            # writing the fields 
            csvwriter.writerow(likesResponseHeading) 
                
            # writing the data rows 
            csvwriter.writerows(likesResponseArray)
        
        fName =  username + "" + "_retweet_analysis_" + date_time + ".csv"    
        with open(fName, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
                
            # writing the fields 
            csvwriter.writerow(reTweetResponseArrayHeading) 
                
            # writing the data rows 
            csvwriter.writerows(reTweetResponseArray)

        fName =  username + "" + "_comment_analysis_" + date_time + ".csv"    
        with open(fName, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
                
            # writing the fields 
            csvwriter.writerow(commentResponseArrayHeading) 
                
            # writing the data rows 
            csvwriter.writerows(commentResponseArray)

        # fName =  username + "" + "_analysis_" + date_time + ".json"
        # with open( fName, 'w', encoding='utf8') as json_file:
        #     json.dump(array, json_file, indent=4)

    except json.decoder.JSONDecodeError as jsonErr:
            logger.error("Could not parse the file:" + outputJsonFile)
            logger.error(f"Unexpected {jsonErr=}, {type(jsonErr)=}")

    except BaseException as err:
            logger.error(f"Unexpected {err=}, {type(err)=}")
    
def analyseDailyData():
    outputPath = '.'
    curDir = os.getcwd();
    logger.info('readJSONFile')
    configParam = readConfig.readConfigurationFile()
    outputPath = configParam[constants.OUTPUT_PATH]

    outputFiles = os.listdir(outputPath)

    print("Files and directories in '", outputPath, "' :")

    # prints all files
    print(outputPath)
    validFileList = []
    for file in outputFiles:
        match = re.search("\.json$", file)
        if match:
            print("The file ending with .json is:", file)
            validFileList.append(file)

    if(len(validFileList)):
        for file in validFileList:
            # readJSONFile( jsonFolder + "/" + file)
            readOutputJSONFile(outputPath + "/" + file)        
def main(): 
    logger.info('Started')
    analyseDailyData()
    
if __name__ == '__main__':
    main()
