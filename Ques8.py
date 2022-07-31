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
vaccination_data=vaccination_data[['State_Code','District_Key','District','14/08/2021.3','14/08/2021.4']]

# Rename vaccination data cloumns

vaccination_data.rename(columns={'State_Code': 'stateid','District_Key': 'districtid','District': 'Name'	,'14/08/2021.3': 'First Dose', '14/08/2021.4': 'Second Dose'}, inplace=True)

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

def overall_ratio(common_data):
    overall_data=common_data[['First Dose','Second Dose','TOT_P']]
    overall_data=overall_data.astype({'First Dose': float, 'Second Dose': float,'TOT_P': float})

    vaccinateddose1ratio=overall_data['First Dose'].sum()/overall_data['TOT_P'].sum()
    vaccinateddose2ratio=overall_data['Second Dose'].sum()/overall_data['TOT_P'].sum()
  
    with open('overall-vaccinated-dose-ratio.csv','w') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['Country','vaccinateddose1ratio','vaccinateddose2ratio'])
        csv_out.writerow(('India',vaccinateddose1ratio,vaccinateddose2ratio))

overall_ratio(common_data)

def statewise_ratio(common_data):
    state_wise_data = common_data[['stateid','First Dose','Second Dose','TOT_P']]
    state_wise_data=state_wise_data.astype({'First Dose': float, 'Second Dose': float,'TOT_P': float})

    state_wise_data=state_wise_data.groupby(state_wise_data['stateid'], as_index=False).aggregate({'First Dose': 'sum', 'Second Dose': 'sum', 'TOT_P': 'sum'}).reindex(columns=state_wise_data.columns)

    for i in range(len(common_data)):
        state_wise_data['vaccinateddose1ratio']=state_wise_data['First Dose'] / state_wise_data['TOT_P']
        state_wise_data['vaccinateddose2ratio']=state_wise_data['Second Dose'] / state_wise_data['TOT_P']  
    
    state_wise_data=state_wise_data.drop(['First Dose', 'Second Dose','TOT_P'], axis = 1)
    
    state_wise_data=state_wise_data.sort_values('vaccinateddose1ratio')
    
    state_wise_data.to_csv('state-vaccinated-dose-ratio.csv', index=False)

statewise_ratio(common_data)

def districtwise_ratio(common_data):
    
    district_wise_data = common_data[['districtid', 'First Dose', 'Second Dose','TOT_P']]
    district_wise_data=district_wise_data.astype({'First Dose': float, 'Second Dose': float,'TOT_P': float})
    
    for i in range(len(common_data)):
        district_wise_data['vaccinateddose1ratio']=district_wise_data['First Dose'] / district_wise_data['TOT_P']
        district_wise_data['vaccinateddose2ratio']=district_wise_data['Second Dose'] / district_wise_data['TOT_P']  
    
    district_wise_data=district_wise_data.drop(['First Dose','Second Dose','TOT_P'], axis = 1)
    
    district_wise_data=district_wise_data.sort_values('vaccinateddose1ratio')

    district_wise_data.to_csv('district-vaccinated-dose-ratio.csv', index=False)

districtwise_ratio(common_data)

