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


# Loading cowin_vaccine_data_districtwise.csv data
vaccine_data_df=pd.read_csv('cowin_vaccine_data_districtwise.csv')

#requires data till 14/08/2021 only   
df1=vaccine_data_df.iloc[:, 0:2116]                         

# Function to return list of relevant columns for this question i.e district id,dose1 ,dose 2 data
def column_generator():
    start=datetime.datetime(2021, 1, 16)
    end=datetime.datetime(2021, 8, 14)
    index=pd.date_range(start, end)
    l=['District_Key']
    for item in index:
        temp1=str(item.strftime('%d/%m/%Y'))+".3"
        temp2=str(item.strftime('%d/%m/%Y'))+".4"
        l.extend([temp1,temp2])
    return l

# Function to write final output to csv file
def save_to_csv(file_name,data,loc_id,time_id):
    data.sort(key=lambda x:x[0])
    with open(file_name,'w') as out:
        csv_out=csv.writer(out)
        csv_out.writerow([loc_id,time_id,'Dose1','Dose2'])
        for row in data:
            csv_out.writerow((row[0],row[1],int(row[2]),(int(row[3]))))

column=column_generator()

df1=df1[column]       #fetching required columns
df1=df1.drop(df1.index[0])

df1[column[1:]]=df1[column[1:]].astype(float)       #converting object to float so that i can replace nan values

df1.replace(np.nan, 0)                #replace nan by 0

df_list = df1.values.tolist()

vaccine={}
for item in df_list:
    key=item.pop(0)
    vaccine[key]=item

dose1_vaccine={}          #store dose 1 data
dose2_vaccine={}          #store dose 2 data

for item in vaccine:
    dose1_vaccine[item]=vaccine[item][::2]                #fetch values from even indices
    dose2_vaccine[item]=vaccine[item][1::2]               #fetch values from odd indices

dose1_vaccine["WB_Uttar Dinajpur"][0]=0.0                 #replacing nan by 0
dose2_vaccine["WB_Uttar Dinajpur"][0]=0.0				  #replacing nan by 0

overall_dose=[]
overall_doses_state=[]

def overall_vaccination():

    state={}
    for item in dose1_vaccine:
        key=item.partition("_")[0]
        if key in state:
            pass
        else:
            state[key]=[0,0]

        overall_dose.append((item,1,int(dose1_vaccine[item][-1]),int(dose2_vaccine[item][-1])))
        state[key][0]+=int(dose1_vaccine[item][-1])
        state[key][1]+=int(dose2_vaccine[item][-1])

    for item in state:
        overall_doses_state.append((item,1,state[item][0],state[item][1]))

overall_vaccination()

save_to_csv('vaccinated-count-overall.csv',overall_dose,'DistrictId','OverallId')

save_to_csv('state-vaccinated-count-overall.csv',overall_doses_state,'StateId','OverallId')

weekly_doses=[]
weekly_doses_state=[]

def weekly_vaccination():

    for c in range(1,31):
        state={}
        for item in dose1_vaccine:
            key=item.partition("_")[0]
            if key in state:
                pass
            else:
                state[key]=[0,0]
        
            d1=(dose1_vaccine[item][c*7])-(dose1_vaccine[item][c*7-7])
            d2=(dose2_vaccine[item][c*7])-(dose2_vaccine[item][c*7-7])
            state[key][0]+=d1
            state[key][1]+=d2
            weekly_doses.append((item,c,d1,d2))

        for item in state:
            weekly_doses_state.append((item,c,state[item][0],state[item][1]))

weekly_vaccination()

save_to_csv('vaccinated-count-week.csv',weekly_doses,'DistrictId','WeekId')

save_to_csv('state-vaccinated-count-week.csv',weekly_doses_state,'StateId','WeekId')


monthly_doses=[]
monthly_doses_state=[]
month_st=[0,30,58,89,119,150,180]
month_end=[29,57,88,118,149,179,210]

def monthly_vaccination():
    
    # For 1st month  i.e 15/01/2021 to 14/02/2021

    state={}
    for item in dose1_vaccine:

        key=item.partition("_")[0]
        if key in state:
            pass
        else:
            state[key]=[0,0]

        d1=(dose1_vaccine[item][29])
        d2=(dose2_vaccine[item][29])
        monthly_doses.append((item,1,d1,d2))
        state[key][0]+=d1
        state[key][1]+=d2

    for item in state:
        monthly_doses_state.append((item,1,state[item][0],state[item][1]))

    # From 2nd month onwards

    for m in range(1,7):
        state={}
        for item in dose1_vaccine:
            key=item.partition("_")[0]
            if key in state:
                pass
            else:
                state[key]=[0,0]

            d1=(dose1_vaccine[item][month_end[m]])-(dose1_vaccine[item][month_st[m]-1])
            d2=(dose2_vaccine[item][month_end[m]])-(dose2_vaccine[item][month_st[m]-1])
            monthly_doses.append((item,m+1,d1,d2))
            state[key][0]+=d1
            state[key][1]+=d2

        for item in state:
            monthly_doses_state.append((item,m+1,state[item][0],state[item][1]))

monthly_vaccination()

save_to_csv('vaccinated-count-month.csv',monthly_doses,'DistrictId','MonthId')

save_to_csv('state-vaccinated-count-month.csv',monthly_doses_state,'StateId','MonthId')


