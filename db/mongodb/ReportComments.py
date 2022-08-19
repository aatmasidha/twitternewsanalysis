'''
Created on 27-Jul-2022
@author: m_atm
'''
import csv
import pymongo
import re
import os
import pandas as pd
import configparam.constants as constants
import configparam.readconfigparam as readConfig

def populateTweetData():
    try:
        
        # configParam = readConfig.readConfigurationFile()
        # outputPath = configParam[constants.OUTPUT_PATH]
        outputPath = "C:/Users/m_atm/OneDrive - University of Dundee/Semester - II/MScProject/NewsSentimentDataAnalysis/out"
                
        # getCommentsData()
        getCommentsCountsForEachComment()
                # validFileList.append(file)
    except KeyError as err:
            print(f"Unexpected {err=}, {type(err)=}")
    except pymongo.errors.DuplicateKeyError as duplicateKey:
            print(f"Unexpected {duplicateKey=}, {type(duplicateKey)=}")        
    except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")

def getCommentsCountsForEachComment():
    try: 

        configParam = readConfig.readConfigurationFile()
        databaseName = configParam[constants.DATABASE_NAME]
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
        # mydb = myclient['twitteremotiondb']
        # print("twitteremotioncollection:", mydb)
        # mycol = mydb['tweetsdata']

        result = myclient[databaseName]['tweetsdata'].aggregate([
                    {
                        '$lookup': {
                            'from': 'commenttweetsdata', 
                            'localField': '_id', 
                            'foreignField': 'NewsRef', 
                            'as': 'commentuser'
                        }
                    }
                ])
            
        original_df = pd.DataFrame(result)  
        original_df 
        # for key, value in original_df.iteritems():
        #     print(key, value)
        #     print()
        listComments = list()  
        for rowVal in original_df.itertuples():
            basicRow = []
            basicRow.append(getattr(rowVal, "_1"))
            basicRow.append(getattr(rowVal, "NewsHeadLine"))
            basicRow.append(getattr(rowVal, "NewsCategory"))
            basicRow.append(getattr(rowVal, "BertEmotion"))
            basicRow.append(getattr(rowVal, "Text2Emotion"))
            basicRow.append(getattr(rowVal, "NewsSensitivity"))
            basicRow.append(getattr(rowVal, "NewsPolarity"))
            basicRow.append(getattr(rowVal, "NewsHandler"))
            commentsArray = getattr(rowVal, "commentuser")
            commentDict = {'Love':0,'Fear':0,'Joy':0, 'Sadness':0, 'Surprise':0, 'Anger':0 }
            if(len(commentsArray) > 0):
                for i in range (len(commentsArray)):
                    print (commentsArray[i])
                    key = commentsArray[i]['Emotion']
                    if key in commentDict.keys():       
                        commentDict[key] = commentDict[key] + 1
                    else:
                        commentDict[key] = 1
                        
            for emotionCount in commentDict.values():
                print(emotionCount)
                basicRow.append(emotionCount)            
            listComments.append(basicRow )
                    
        columns = ['NewsID','Text','NewsCategory', 'BertEmotion', 'Text2Emotion', 'NewsSensitivity', 'NewsPolarity','NewsHandler', 'LoveCnt','FearCnt','JoyCnt', 'SadnessCnt', 'SurpriseCnt', 'AngerCnt']
        
        df = pd.DataFrame (listComments)
        df.columns = columns
        df.to_csv('commentsbyuser.csv')
        print (df)
        
        correlations = df.corr()
        correlations
        # Make the figsize 7 x 6
        # plt.figure(figsize=(7,6))
        # Plot heatmap of correlations
        # sns.heatmap(correlations)
        # plt.show()
    except KeyError as err:
        print(f"Unexpected {err=}, {type(err)=}")
    except pymongo.errors.DuplicateKeyError as duplicateKey:
            print(f"Unexpected {duplicateKey=}, {type(duplicateKey)=}")        
    except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            
            

def getCommentsData():
    try: 
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
        # mydb = myclient['twitteremotiondb']
        # print("twitteremotioncollection:", mydb)
        # mycol = mydb['tweetsdata']

        result = myclient['twitteremotiondb']['tweetsdata'].aggregate([
                    {
                        '$lookup': {
                            'from': 'commenttweetsdata', 
                            'localField': '_id', 
                            'foreignField': 'NewsRef', 
                            'as': 'commentuser'
                        }
                    }
                ])
            
        original_df = pd.DataFrame(result)  
        original_df 
        # for key, value in original_df.iteritems():
        #     print(key, value)
        #     print()
        listComments = list()  
        for rowVal in original_df.itertuples():
            basicRow = []
            basicRow.append(getattr(rowVal, "_1"))
            basicRow.append(getattr(rowVal, "NewsCategory"))
            basicRow.append(getattr(rowVal, "BertEmotion"))
            basicRow.append(getattr(rowVal, "Text2Emotion"))
            basicRow.append(getattr(rowVal, "NewsSensitivity"))
            basicRow.append(getattr(rowVal, "NewsPolarity"))
            basicRow.append(getattr(rowVal, "NewsHandler"))
            commentsArray = getattr(rowVal, "commentuser")
            if(len(commentsArray) > 0):
                for i in range (len(commentsArray)):
                    print (commentsArray[i])
                    likeRow = []
                    # likeRow.append(basicRow)
                    likeRow.append(commentsArray[i]['CommentUserName'])
                    likeRow.append(commentsArray[i]['Emotion'])
                    likeRow.append(commentsArray[i]['Location'])
                    likeRow.append(commentsArray[i]['CreatedAt'])
                    # listLikes.append(likeRow)
                    listComments.append(basicRow + likeRow)
                    print(likeRow)         
        
        columns = ['NewsID','NewsCategory', 'BertEmotion', 'Text2Emotion', 'NewsSensitivity', 'NewsPolarity','NewsHandler', 'CommentUserName', 'Emotion', 'Location','CreatedAt']
        
        df = pd.DataFrame (listComments)
        df.columns = columns
        df.to_csv('comments.csv')
        print (df)    
        

    except KeyError as err:
        print(f"Unexpected {err=}, {type(err)=}")
    except pymongo.errors.DuplicateKeyError as duplicateKey:
            print(f"Unexpected {duplicateKey=}, {type(duplicateKey)=}")        
    except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
    
if __name__ == '__main__':
    populateTweetData()