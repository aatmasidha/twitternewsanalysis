'''
Created on 27-Jul-2022
@author: m_atm
'''
import csv
import pymongo
import re
import os

def populateTweetData():
    try:
        
        # configParam = readConfig.readConfigurationFile()
        # outputPath = configParam[constants.OUTPUT_PATH]
        outputPath = "C:/Users/m_atm/OneDrive - University of Dundee/Semester - II/MScProject/NewsSentimentDataAnalysis/out"
        jsonOutputFiles = os.listdir(outputPath)
     
        print("Files and directories in '", outputPath, "' :")
        validFileList = []

        for valFile in jsonOutputFiles:
            # match = re.search("\.csv", file)
            match = re.search(r'\d{4}_\d{2}_\d{2}_T_\d{2}_\d{2}_\d{2}.csv', valFile)
            if match:
                print("The file ending with .json is:", valFile)
                # match = re.search(r'\d{4}_\d{2}_\d{2}_T_\d{2}_\d{2}_\d{2}', file)
                # date = datetime.strptime(match.group(), '%Y_%m_%d_T_%H_%M_%S')
                # if match:
                validFileList.append(valFile)
                    
                # validFileList.append(file)
        for csvFile in validFileList:
            if(csvFile.find("comment")!=-1):
                commentResponseArrayHeading = ['UserID', 'Comment','Emotion','CommentUserName', 'Location', 'CreatedAt','NewsRef']
                # fileName = '../../out/AJEnglish_comment_analysis_2022_07_29_T_07_34_33.csv'
                # fileName = '../../out/' + csvFile
                fileName = './out/' + csvFile
                print(fileName)     
                insertToMangoDB(fileName, "commenttweetsdata", commentResponseArrayHeading)
            elif(csvFile.find("likes")!=-1):
                likesResponseHeading = ['UserID', 'LikesUserName', 'Location', 'CreatedAt','NewsRef']
                # fileName = '../../out/AJEnglish_likes_analysis_2022_07_29_T_07_34_33.csv'
                # fileName = '../../out/' + csvFile
                fileName = './out/' + csvFile
                print(fileName)     
                insertToMangoDB(fileName, "likestweetsdata", likesResponseHeading)
            elif(csvFile.find("retweet")!=-1):
                reTweetResponseArrayHeading = ['UserID', 'ReTweetUserName', 'Location', 'CreatedAt','NewsRef']
                # fileName = '../../out/AJEnglish_retweet_analysis_2022_07_29_T_07_34_33.csv'
                # fileName = '../../out/' + csvFile
                fileName = './out/' + csvFile
                print(fileName)
                insertToMangoDB(fileName, "retweettweetsdata", reTweetResponseArrayHeading)
            else:
                newsAnalysisHeading = ['NewsID', 'NewsHeadLine', 'NewsSensitivity','NewsCategory', 'NewsPolarity','BertEmotion', 'Text2Emotion',  'NumReTweets', 'RetweetIds', 'NumLikes', 'LikeIds', 'NumComments', 'CommentIDs','CreatedAt','NewsHandler']        
                # fileName = '../../out/AJEnglish_analysis_2022_07_29_T_07_34_33.csv'
                # fileName = '../../out/' + csvFile
                fileName = './out/' + csvFile
                print(fileName)     
                insertToMangoDB(fileName, "tweetsdata", newsAnalysisHeading)    
    except KeyError as err:
            print(f"Unexpected {err=}, {type(err)=}")
    except pymongo.errors.DuplicateKeyError as duplicateKey:
            print(f"Unexpected {duplicateKey=}, {type(duplicateKey)=}")        
    except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")


def insertToMangoDB(csvFile, collectionName, header):
    try: 
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
        mydb = myclient['newsemotionanalysis']
        print("twitteremotioncollection:", mydb)
        mycol = mydb[collectionName]
        
        # if(collectionName != 'tweetsdata'):
        #     mycol.create_index('ID','Created At', unique = True) 
        # if(collectionName == 'commenttweetsdata'):
        #     mycol.create_index([('commentID', 1), ('CreatedAt', 1)], unique=True)
        if(collectionName != 'tweetsdata'):
            mycol.create_index([('UserID', 1), ('NewsRef', 1)], unique=True)
            # mycol.drop_index( { '_id_': 1 } )
                
        file = open(csvFile, 'r')
        reader = csv.DictReader( file )
        tweetArray = []
        for each in reader:
            row={}
            newsID = ''
            for field in header:
                
                if(field== 'NewsID'): 
                    newsID = each[field]
                    if(len(newsID) > 0):
                        row['_id'] = each[field]
                    else:
                        break
                # if(field== 'commentID'): 
                #     commentID = each[field]
                #     if(len(commentID) > 0):
                #         row['_id'] = each[field]
                #     else:
                #         break
                # if(field== 'ID'): 
                #     likeRetweetId = each[field]
                #     if(len(likeRetweetId) > 0):
                #         row['_id'] = each[field]
                #     else:
                #         break
                else:                             
                    row[field] = each[field]
                    if(field == 'LikeIds' or field == 'CommentIDs' or field == 'RetweetIds'):
                         text = row[field].replace('\'', '')
                         text = text.replace('[', '')
                         text = text.replace(']', '')

                         words = text.split()
                         for current_word in words:
                             print(current_word)
                         my_list = [] # make empty list
                         for current_word in words:
                            current_word = current_word.replace(',', '')
                            my_list.append(current_word.lower())
                         row[field] = my_list
                    if( len(row[field]) <= 0 ):
                        row[field] = 'empty'
            if(len(newsID) > 0):
                myquery = { "_id":  row['_id']}
                oldRecord = mycol.find(myquery)
                rec = ''
                for x in oldRecord:
                    print(x)
                    rec = x
                # if( len(rec) > 0):
                #     continue
                # else:
                #     tweetArray.append(row)
                
                if( len(rec) <= 0):
                    tweetArray.append(row)


            else:
                myquery = { "UserID":  row['UserID'], "NewsRef":  row['NewsRef']}
                oldRecord = mycol.find(myquery)
                rec = ''
                for x in oldRecord:
                    print(x)
                    rec = x
                # if( len(rec) > 0):
                #     continue
                # else:
                #     tweetArray.append(row)
                if( len(rec) <= 0):
                    tweetArray.append(row)
        
        if( len(tweetArray) > 0 ):
            records = mycol.insert_many(tweetArray)
            print(records.inserted_ids)
            
    except KeyError as err:
            print(f"Unexpected {err=}, {type(err)=}")
    except pymongo.errors.DuplicateKeyError as duplicateKey:
            print(f"Unexpected {duplicateKey=}, {type(duplicateKey)=}")        
    except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
    
if __name__ == '__main__':
    populateTweetData()