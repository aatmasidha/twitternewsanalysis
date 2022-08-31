# twitternewsanalysis
This program get data from Twitter USING Twitter API 2. One needs to add API key with environment variable as BEARER_KEY. It needs the folder dailydata and out folder.

Data from Twitter will be stored in JSON format in the dailydata and then processed data will be stored in the out folder in csv format.

a.	FlowController.py --getdata True => gets data from twitter.  

b.	FlowController.py -- preparedata  True => data cleaning is done

c.	FlowController.py -- analysedata True => data is analysed

d.	FlowController.py -- populatedata True => populated the data in mongodb

FlowController is the overall controlling program to get analysed data.
