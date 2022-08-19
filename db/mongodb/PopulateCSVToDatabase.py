import json
import logging
import os
import re

from jproperties import Properties
import nltk

# import bbcnews
nltk.download('omw-1.4')
import configparam.readconfigparam as readConfig
import configparam.constants as constants
import pymongo
import csv

logger = logging.getLogger(__name__)
# logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

configs = Properties()

def insertToMangoDB(jsonDump):
    try: 
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
        mydb = myclient['twetteranalyse']
        print("twetteranalyse:", mydb)
        header = [ "name", "age", "country"]
        csvfile = open('employee.csv', 'r')
        reader = csv.DictReader( csvfile )
        
        for each in reader:
            row={}
            for field in header:
                row[field]=each[field]
        
            print (row)
    # db.segment.insert(row)
    
    
        
        
        mycol = mydb["tweetsdata"]
        tweetArray = []
        for tweet in jsonDump:
            print(tweet)
            tweet = re.sub("newsId","_id", json.dumps(tweet))
            tweet = json.loads(tweet)
            id = tweet["_id"]
            myquery = { "_id": id }
            oldRecord = mycol.find(myquery)
            rec = ''
            for x in oldRecord:
                print(x)
                rec = x
            if( len(rec) > 0):
                continue
            else:
                tweetArray.append(tweet)
            
        if( len(tweetArray) > 0 ):
            records = mycol.insert_many(tweetArray)
            print(records.inserted_ids)
        
    except pymongo.errors.DuplicateKeyError as duplicateKey:
            logger.error(f"Unexpected {duplicateKey=}, {type(duplicateKey)=}")        
    except BaseException as err:
            logger.error(f"Unexpected {err=}, {type(err)=}")


def readFilesFromDailyPath():
    try:
        configParam = readConfig.readConfigurationFile()
        outputPath = configParam[constants.OUTPUT_PATH]
        jsonOutputFiles = os.listdir(outputPath)
     
        print("Files and directories in '", outputPath, "' :")
    
        # prints all files
        print(jsonOutputFiles)
        validFileList = []
        for file in jsonOutputFiles:
            match = re.search("\.json$", file)
            if match:
                print("The file ending with .json is:", file)
                validFileList.append(file)
             
        if(len(validFileList)):
            for file in validFileList:
                fileName = outputPath + "/" + file
                with open(fileName) as json_file:
                    data = json.load(json_file)
                    insertToMangoDB(data)
                    
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


