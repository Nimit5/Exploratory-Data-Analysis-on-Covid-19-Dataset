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


vaccine_data_df=pd.read_csv('cowin_vaccine_data_districtwise.csv')
vaccine_data_df=vaccine_data_df.iloc[:, 0:2116]

vaccine_data=vaccine_data_df[["State_Code","District_Key","14/08/2021.8","14/08/2021.9"]]

vaccine_data.rename(columns={'State_Code':'stateid','District_Key':'districtid','14/08/2021.8':'Covaxin','14/08/2021.9':'CoviShield'}, inplace=True)
vaccine_data=vaccine_data.drop(vaccine_data.index[0])


def overall_ratio(vaccine_data):

    overall_data=vaccine_data[['Covaxin','CoviShield']]
    overall_data=overall_data.astype({'Covaxin': float,'CoviShield':float})

    vaccineratio=overall_data['CoviShield'].sum()/overall_data['Covaxin'].sum()
    
    with open('overall-vaccine-type-ratio.csv','w') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['Country','vaccineratio'])
        csv_out.writerow(('India',vaccineratio))


overall_ratio(vaccine_data)


def statewise_ratio(vaccine_data):

    state_wise_data=vaccine_data[['stateid','Covaxin','CoviShield']]
    state_wise_data=state_wise_data.astype({'Covaxin': float,'CoviShield':float})

    state_wise_data=state_wise_data.groupby(state_wise_data['stateid'], as_index=False).aggregate({'Covaxin':'sum','CoviShield':'sum'}).reindex(columns=state_wise_data.columns)
   
    for i in range(len(state_wise_data)):
        state_wise_data['vaccineratio'] = state_wise_data['CoviShield'] / state_wise_data['Covaxin']
        
    state_wise_data=state_wise_data.drop(['Covaxin','CoviShield'], axis = 1)
    
    state_wise_data=state_wise_data.sort_values('vaccineratio')

    state_wise_data.replace(np.inf, "N/A", inplace=True)
    
    state_wise_data.to_csv('state-vaccine-type-ratio.csv', index=False)


statewise_ratio(vaccine_data)


def district_wise_ratio(vaccine_data):
    district_wise_data=vaccine_data[['districtid','Covaxin','CoviShield']]
    district_wise_data=district_wise_data.astype({'Covaxin': float,'CoviShield':float})

    for i in range(len(district_wise_data)):
          district_wise_data['vaccineratio']=district_wise_data['CoviShield'] / district_wise_data['Covaxin']
    
    district_wise_data=district_wise_data.drop(['Covaxin','CoviShield'], axis = 1)

    district_wise_data=district_wise_data.sort_values('vaccineratio')

    district_wise_data.replace(np.inf, "N/A", inplace=True)

    district_wise_data.to_csv('district-vaccine-type-ratio.csv', index=False)

district_wise_ratio(vaccine_data)


