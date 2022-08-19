from datetime import datetime
import json
import logging
import os
import re

from jproperties import Properties
import nltk
from nltk.corpus import subjectivity
from transformers import pipeline

import configparam.constants as constants
import configparam.readconfigparam as readConfig
from model.naivebayesclassifer import bbcnews
import text2emotion as te
from utils import ProcessText



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
        # finalMap = {}
        processMap = {}
        array = []
        # with open(outputJsonFile) as json_file:
        #         data = json.loads(json_file.read())
        
        # with open(outputJsonFile) as json_file:
        #     data = json.load(json_file)
        #     print(len(data))
        # for item in data:
        fileObject = open(outputJsonFile, "r")
        jsonContent = fileObject.read()
        aList = json.loads(jsonContent)
        for item in aList:
            for keyData, valueData in item.items():
                if(keyData == "text"):
                    text = valueData
                    if(len(str(text)) != 0):
                        model_id = "aatmasidha/distilbert-base-uncased-finetuned-emotion"
                        bertClassifier = pipeline("text-classification", model=model_id)
                        preds = bertClassifier(text, return_all_scores=True)
                        print(preds)
            
                        processMap['bert_headline'] = preds
                        emotion_value = emotion_detection_text2emotion(text)
                        processMap['package_headline'] = emotion_value
                    else:
                        processMap['bert_headline'] = 'NA'
                        processMap['package_headline'] = 'NA'       
            
                    classifier = bbcnews.classifier(text)
                    processMap['classifier'] = classifier                    
                    subjectivity = ProcessText.getSubjectivity(text)
                    processMap['subjectivity'] = ProcessText.getSubjectivity(text)
                    polarity = getAnalysis(ProcessText.getPolarity(text))  
                    processMap['polarity'] = polarity
                else:
                    processMap[keyData] = valueData
            array.append(processMap)
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
        
        fName =  username + "" + "_analysis_" + date_time + ".json"
        with open( fName, 'w', encoding='utf8') as json_file:
            json.dump(array, json_file, indent=4)

    except json.decoder.JSONDecodeError as jsonErr:
            logger.error("Could not parse the file:" + outputJsonFile)
            logger.error(f"Unexpected {jsonErr=}, {type(jsonErr)=}")

    except BaseException as err:
            logger.error(f"Unexpected {err=}, {type(err)=}")
    
def analyseDailyData():
    # outputPath = '.'
    # curDir = os.getcwd();
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
