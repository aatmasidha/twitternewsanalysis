import pandas as  pd




newsData=pd.read_csv("C:/Users/m_atm/OneDrive - University of Dundee/Semester - II/MScProject/NewsSentimentDataAnalysis/tweetscompletedata.csv")
print(newsData.head())


# Cross tabulation between GENDER and APPROVE_LOAN
CrosstabResult=pd.crosstab(index=newsData['NewsPolarity'],columns=newsData['NewsCategory'])
print(CrosstabResult)



# importing the required function
from scipy.stats import chi2_contingency

# Performing Chi-sq test
ChiSqResult = chi2_contingency(CrosstabResult)

# P-Value is the Probability of H0 being True
# If P-Value&gt;0.05 then only we Accept the assumption(H0)

print('The P-Value of the ChiSq Test is:', ChiSqResult[1])