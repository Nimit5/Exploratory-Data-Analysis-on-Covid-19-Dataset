# Importing libraries 

import json
import csv
import requests
import pandas as pd
import numpy as np
import datetime
import math
import warnings 
warnings.filterwarnings('ignore')


# Vaccination data

vaccination_data=pd.read_csv("cowin_vaccine_data_districtwise.csv")
vaccination_data=vaccination_data[['State_Code','District_Key','District','07/08/2021.3','14/08/2021.3']]


# Rename vaccination data cloumns

vaccination_data.rename(columns={'State_Code':'stateid','District_Key': 'districtid','District': 'Name'	,'07/08/2021.3': 'First Dose 7 Aug','14/08/2021.3': 'First Dose 14 Aug'}, inplace=True)

# Drop empty data row
vaccination_data.drop(0)

# Census Data
df=pd.read_excel("DDW_PCA0000_2011_Indiastatedist.xlsx")

df=df[["Level","Name","TRU","TOT_P"]]


# District wise census data
district_census=df[(df["Level"]=="DISTRICT") & (df["TRU"]=="Total") ]


#Removing extra spaces from District Name 
district_census['Name']=district_census['Name'].str.strip()

# Manually created Census_Correction.csv which contains {wrong:correct} pairs
df=pd.read_csv('Census_Correction.csv') 
correction=pd.Series(df.Correct.values,index=df.Wrong).to_dict()


#Correcting Names of districts in dataframe using correction dictionary
district_census['Name']=district_census['Name'].map(correction).fillna(district_census['Name'])


#List of districts present in census
cenus_districts=district_census['Name'].values

# Fetching data of only common districs between census data and vaccination data
common_data=vaccination_data.loc[vaccination_data['Name'].isin(cenus_districts)]

# Merge Both data
common_data=pd.merge(common_data,district_census,on='Name')

common_data=common_data.drop_duplicates(subset =["districtid","Name"])

# Dropping unnecessary columns
common_data=common_data.drop(['TRU','Level','Name'], axis = 1)


# Function to generate dates from 14/08/2021 
def date_generator():
    start=datetime.datetime(2021, 8, 14)
    end=datetime.datetime(2026, 12, 31)
    index=pd.date_range(start, end)
    l=[]
    for item in index:
        temp=item.date()
        l.append(temp)
    return l

#Fuction to compute complete vaccination of states
def complete_vaccination(common_data):
    state_wise_data = common_data[['stateid','First Dose 7 Aug','First Dose 14 Aug','TOT_P']]
    state_wise_data=state_wise_data.astype({'First Dose 7 Aug': float,'First Dose 14 Aug': float,'TOT_P': float})
    state_wise_data=state_wise_data.groupby(state_wise_data['stateid'], as_index=False).aggregate({'First Dose 7 Aug': 'sum','First Dose 14 Aug': 'sum','TOT_P': 'sum'}).reindex(columns=state_wise_data.columns)
    state_wise_data['populationleft'] = state_wise_data['TOT_P']-state_wise_data['First Dose 14 Aug']
    state_wise_data['populationleft'] =state_wise_data['populationleft'].clip(lower=0)
    state_wise_data['rateofvaccination(per week)'] = state_wise_data['First Dose 14 Aug']-state_wise_data['First Dose 7 Aug']
    dates=date_generator()
    expected_date=[]
    no_of_weeks_needed=state_wise_data['populationleft']/state_wise_data['rateofvaccination(per week)']

    for i in range(len(no_of_weeks_needed)):
        no_of_days_needed=int(math.ceil(no_of_weeks_needed[i]*7))
        expected_date.append(dates[no_of_days_needed])
    
    state_wise_data['date']=pd.DataFrame(expected_date)
    
    # Dropping unnecessary columns
    state_wise_data=state_wise_data.drop(['First Dose 7 Aug','First Dose 14 Aug','TOT_P'], axis = 1)
    
    #save to complete-vaccination.csv
    state_wise_data.to_csv('complete-vaccination.csv', index=False)

complete_vaccination(common_data)


