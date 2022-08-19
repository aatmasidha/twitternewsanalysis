import argparse
import logging

# import debugpy
# from debugpy.common.json import default
from jproperties import Properties
# from pipenv.patched.notpip._internal.utils import distutils_args
import os
from preparedata import createdataforanalysis
from tweetdataextract import tweeterdatahandler
from analysetweetdata import classifydata2csv as  classifydata
from db.mongodb import populatetodb
from db.mongodb import ReportComments
curdir = os.getcwd()
logging.config.fileConfig('./configparam/logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)
configs = Properties()
    
#virtual colonisation are we able to proove

#This is the main entrance file which controls the flow of the program. The module takes 3 input parameters
#if use does not set any parameter then by default only the data from twitter handlers is read.  
# Data is not analysed by default. 
#it takes the parameters to understand if user wants to get data from twitter
#

def parseArguments():
    argDict = {'getdata':False, 'preparedata':False, 'analysedata':True, 'populatetodbdata':True, 'reportdata' : False  }
    try:
        parser = argparse.ArgumentParser(description="Arguments For Tweet Extraction and  Analysis",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("--getdata", help="Get data from Twitter", default=False)
        parser.add_argument("--preparedata", help="Clean and filter twitter data for analysis", default=False)
        parser.add_argument("--analysedata", help="Analyse data", default=False)
        parser.add_argument("--populatetodbdata", help="Populate data to MongoDB", default=False)
        parser.add_argument("--reportdata", help="Generate report from MongoDB", default=False)
        
        args = parser.parse_args()
        print(args.getdata)
        
        argDict['getdata'] = bool(args.getdata)
        argDict['preparedata'] = bool(args.preparedata)
        argDict['analysedata'] = bool(args.analysedata)
        argDict['populatetodbdata'] = bool(args.populatetodbdata)
        argDict['reportdata'] = bool(args.reportdata)
        return argDict
    
    except BaseException as err:
        logger.error(f"Unexpected {err=}, {type(err)=}")
        raise TypeError(f"Unexpected {err=}, {type(err)=}")
    
def main():
    logger.debug("Hello World!")
    try: 
        argDict = argumentsForProcessing = parseArguments()
        if(argDict['getdata'] == True):
            tweeterdatahandler.getNewsDataFromTwitterHandlers()
            logger.debug("getdata")
        if(argDict['preparedata'] == True):  
            createdataforanalysis.readFilesFromDailyPath()
            logger.debug("preparedata")
        if(argDict['analysedata'] == True):  
            classifydata.analyseDailyData()  
            logger.debug("analysedata")            
        if(argDict['populatetodbdata'] == True):  
            populatetodb.populateTweetData()
            logger.debug("populatetodbdata")
        if(argDict['reportdata'] == True):
            ReportComments.populateTweetData()
            logger.debug("reportdata")
        
        logger.debug(argDict)
    except BaseException as err:
        logger.error(f"Unexpected {err=}, {type(err)=}")
        raise TypeError(f"Unexpected {err=}, {type(err)=}")

if __name__ == "__main__":
    main()
