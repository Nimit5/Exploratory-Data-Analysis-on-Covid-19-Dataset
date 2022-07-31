# Importing libraries 

import json
import csv
import requests
import pandas as pd
import numpy as np
import datetime
from math import isnan
import warnings 
warnings.filterwarnings('ignore')

# Vaccination data

vaccination_data=pd.read_csv("cowin_vaccine_data_districtwise.csv")
vaccination_data=vaccination_data[['State_Code','District_Key','District','14/08/2021.5','14/08/2021.6']]

# Rename vaccination data cloumns

vaccination_data.rename(columns={'State_Code':'stateid','District_Key': 'districtid','District': 'Name'	,'14/08/2021.5': 'Male Vaccinated', '14/08/2021.6': 'Female Vaccinated'}, inplace=True)

# Drop empty data row
vaccination_data.drop(0)

# Census Data

df=pd.read_excel("DDW_PCA0000_2011_Indiastatedist.xlsx")

df=df[["Level","Name","TRU","TOT_P","TOT_M","TOT_F"]]

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
    overall_data=common_data[['Male Vaccinated','Female Vaccinated','TOT_M','TOT_F']]
    overall_data=overall_data.astype({'Male Vaccinated':float, 'Female Vaccinated':float,'TOT_M':float,'TOT_F':float})

    vaccinationratio=overall_data['Female Vaccinated'].sum()/overall_data['Male Vaccinated'].sum()
    populationratio=overall_data['TOT_F'].sum()/overall_data['TOT_M'].sum()
    ratioofratios=vaccinationratio/populationratio

    with open('overall-vaccination-population-ratio.csv','w') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['Country','vaccinationratio','populationratio','ratioofratios'])
        csv_out.writerow(('India',vaccinationratio,populationratio,ratioofratios))

overall_ratio(common_data)

def statewise_ratio(common_data):
    state_wise_data = common_data[['stateid', 'Male Vaccinated', 'Female Vaccinated','TOT_M','TOT_F']]
    state_wise_data=state_wise_data.astype({'Male Vaccinated': float, 'Female Vaccinated': float,'TOT_M': float,'TOT_F': float})

    state_wise_data=state_wise_data.groupby(state_wise_data['stateid'], as_index=False).aggregate({'Male Vaccinated':'sum','Female Vaccinated':'sum','TOT_M':'sum','TOT_F':'sum'}).reindex(columns=state_wise_data.columns)

    for i in range(len(common_data)):
        state_wise_data['vaccinationratio'] = state_wise_data['Female Vaccinated'] / state_wise_data['Male Vaccinated']
        state_wise_data['populationratio'] = state_wise_data['TOT_F'] / state_wise_data['TOT_M']  
        state_wise_data['ratioofratios'] = state_wise_data['vaccinationratio'] / state_wise_data['populationratio']
    
    state_wise_data=state_wise_data.drop(['Male Vaccinated','Female Vaccinated','TOT_M','TOT_F'], axis = 1)
    
    state_wise_data=state_wise_data.sort_values('ratioofratios')
    
    state_wise_data.to_csv('state-vaccination-population-ratio.csv', index=False)

statewise_ratio(common_data)

def districtwise_ratio(common_data):
    
    district_wise_data = common_data[['districtid', 'Male Vaccinated', 'Female Vaccinated','TOT_M','TOT_F']]
    district_wise_data=district_wise_data.astype({'Male Vaccinated': float, 'Female Vaccinated': float,'TOT_M': float,'TOT_F': float})
    
    for i in range(len(common_data)):
        district_wise_data['vaccinationratio']=district_wise_data['Female Vaccinated'] / district_wise_data['Male Vaccinated']
        district_wise_data['populationratio']=district_wise_data['TOT_F'] / district_wise_data['TOT_M']  
        district_wise_data['ratioofratios']=district_wise_data['vaccinationratio'] / district_wise_data['populationratio']
    
    district_wise_data=district_wise_data.drop(['Male Vaccinated','Female Vaccinated','TOT_M','TOT_F'], axis = 1)
    
    district_wise_data=district_wise_data.sort_values('ratioofratios')

    district_wise_data.to_csv('district-vaccination-population-ratio.csv', index=False)

districtwise_ratio(common_data)

