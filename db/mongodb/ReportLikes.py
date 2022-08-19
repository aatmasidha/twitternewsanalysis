'''
Created on 27-Jul-2022
@author: m_atm
'''
import csv
import pymongo
import re
import os
import pandas as pd

def populateTweetData():
    try:
        
        # configParam = readConfig.readConfigurationFile()
        # outputPath = configParam[constants.OUTPUT_PATH]
        outputPath = "C:/Users/m_atm/OneDrive - University of Dundee/Semester - II/MScProject/NewsSentimentDataAnalysis/out"
        jsonOutputFiles = os.listdir(outputPath)
     
        print("Files and directories in '", outputPath, "' :")
        validFileList = []

        # for valFile in jsonOutputFiles:
        #     # match = re.search("\.csv", file)
        #     match = re.search(r'\d{4}_\d{2}_\d{2}_T_\d{2}_\d{2}_\d{2}.csv', valFile)
        #     if match:
        #         print("The file ending with .json is:", valFile)
        #         # match = re.search(r'\d{4}_\d{2}_\d{2}_T_\d{2}_\d{2}_\d{2}', file)
        #         # date = datetime.strptime(match.group(), '%Y_%m_%d_T_%H_%M_%S')
        #         # if match:
        #         validFileList.append(valFile)
        
        getLikesData()
        
                # validFileList.append(file)
    except KeyError as err:
            print(f"Unexpected {err=}, {type(err)=}")
    except pymongo.errors.DuplicateKeyError as duplicateKey:
            print(f"Unexpected {duplicateKey=}, {type(duplicateKey)=}")        
    except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")


def getLikesData():
    try: 
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
        # mydb = myclient['twitteremotiondb']
        # print("twitteremotioncollection:", mydb)
        # mycol = mydb['tweetsdata']

        result = myclient['twitteremotiondb']['tweetsdata'].aggregate([
            {
                '$lookup': {
                    'from': 'likestweetsdata', 
                    'localField': '_id', 
                    'foreignField': 'NewsRef', 
                    'as': 'likeuser'
                }
            }
        ])
            
        original_df = pd.DataFrame(result)  
        original_df 
        # for key, value in original_df.iteritems():
        #     print(key, value)
        #     print()
        listLikes = list()  
        for rowVal in original_df.itertuples():
            basicRow = []
            basicRow.append(getattr(rowVal, "_1"))
            basicRow.append(getattr(rowVal, "NewsCategory"))
            basicRow.append(getattr(rowVal, "BertEmotion"))
            basicRow.append(getattr(rowVal, "Text2Emotion"))
            basicRow.append(getattr(rowVal, "NewsSensitivity"))
            basicRow.append(getattr(rowVal, "NewsPolarity"))
            basicRow.append(getattr(rowVal, "NewsHandler"))
            likesArray = getattr(rowVal, "likeuser")
            if(len(likesArray) > 0):
                for i in range (len(likesArray)):
                    print (likesArray[i])
                    likeRow = []
                    # likeRow.append(basicRow)
                    likeRow.append(likesArray[i]['LikesUserName'])
                    likeRow.append(likesArray[i]['Location'])
                    likeRow.append(likesArray[i]['CreatedAt'])
                    # listLikes.append(likeRow)
                    listLikes.append(basicRow + likeRow)
                    print(likeRow)         
        
        columns = ['NewsID','NewsCategory', 'BertEmotion', 'Text2Emotion', 'NewsSensitivity', 'NewsPolarity','NewsHandler', 'LikesUserName', 'Location','CreatedAt']
        
        df = pd.DataFrame (listLikes)
        df.columns = columns
        df.to_csv('likes.csv')
        print (df)    
    except KeyError as err:
        print(f"Unexpected {err=}, {type(err)=}")
    except pymongo.errors.DuplicateKeyError as duplicateKey:
            print(f"Unexpected {duplicateKey=}, {type(duplicateKey)=}")        
    except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
    
if __name__ == '__main__':
    populateTweetData()