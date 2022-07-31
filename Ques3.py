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

# state code mapping -Maps state name with state code
def state_Id_Mapping():
    df=pd.read_csv('cowin_vaccine_data_districtwise.csv')
    df=df[["State","State_Code"]].dropna()
    d=pd.Series(df.State_Code.values,index=df.State).to_dict()
    return d

# districts.csv contains data from 26-04-2020 to 02-09-2021
# Filter out Data between 26-04-2020 - 14-08-2021

df=pd.read_csv('districts.csv')
#df=df[["Date","State","District","Confirmed"]]
df['Date']=pd.to_datetime(df['Date'])

end_date='14-08-2021'
mask=(df['Date'] <= end_date)

df=df.loc[mask]

# dates-list of dates between 26-04-2020-14-08-2021

def date_generator():
    start=datetime.datetime(2020, 4, 26)
    end=datetime.datetime(2021, 8, 14)
    index=pd.date_range(start, end)
    l=[]
    for item in index:
        temp=item.date()
        l.append(temp)
    return l

df['District_Id']=df['State']+"_"+df['District']

# Calculating number of cases overall

overall_cases={} 
mask1=(df['Date']=="2021-08-14")
data=df[mask1]

dist_id=data['District_Id'].values

for d in dist_id:
    v=data[data['District_Id']==d]['Confirmed']
    overall_cases[d]=v.values[0]

#Function for replacing State Name with State Code for final outputs and save it to csv file 

state_key_mapping=state_Id_Mapping()


def save_overall_cases():
    p=['Andaman and Nicobar Islands','Goa','Telangana']

    with open('cases-overall.csv','w') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['DistrictId','OverallId','Cases'])
        for item in overall_cases:
            temp=item.partition("_")
            if temp[0] in p:
                key=state_key_mapping[temp[0]]+"_"+temp[0]
            else:
                key=state_key_mapping[temp[0]]+"_"+temp[2]
            csv_out.writerow((key,1,overall_cases[item]))

#To save overall-cases in overall-cases.csv file

save_overall_cases()


# Calculating number of cases per month 

month_end=['2020-05-14', '2020-06-14', '2020-07-14', '2020-08-14', '2020-09-14', '2020-10-14', '2020-11-14','2020-12-14', 
           '2021-01-14', '2021-02-14', '2021-03-14', '2021-04-14', '2021-05-14', '2021-06-14', '2021-07-14','2021-08-14']

monthly_cases=[]

for i in range(len(month_end)):    

    st_day,end_day=i-1,i
    
    if i>0:
        st_data=df[(df['Date']==str(month_end[st_day]))]
        st_dist_id=st_data['District_Id'].values
    
    end_data=df[(df['Date']==str(month_end[end_day]))]
    end_dist_id=end_data['District_Id'].values

    for d in end_dist_id:

        v=end_data[end_data['District_Id']==d]['Confirmed']
        
        if i==0:
              val=v.values[0]

        elif d in st_dist_id:
              v1,v2=st_data[st_data['District_Id']==d]['Confirmed'].values[0],v.values[0]
              val=v2-v1
        else:
            val=v.values[0]
        monthly_cases.append((d,str(i+1),val))

#Function for replacing State Name with State Code for final outputs and save it to csv file 

def save_monthly_cases():
    p=['Andaman and Nicobar Islands','Goa','Telangana']

    with open('cases-month.csv','w') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['DistrictId','MonthId','Cases'])
        for row in monthly_cases:
            temp=row[0].partition("_")
            if temp[0] in p:
                key=state_key_mapping[temp[0]]+"_"+temp[0]
            else:
                key=state_key_mapping[temp[0]]+"_"+temp[2]
            csv_out.writerow((key,row[1],row[2]))

#To save overall-cases in overall-cases.csv file

save_monthly_cases()

# Calculating number of cases per week

dates=date_generator()

no_of_weeks=len(dates)//7

weekly_cases=[]

for i in range(no_of_weeks):

    st_day=i*7

    end_day,prev_end_day=st_day+6,st_day-1
    
    data=df[df['Date']==str(dates[end_day])]
    
    if prev_end_day>=0:

        prev_data=df[df['Date']==str(dates[prev_end_day])]
        
        old_dist_id=prev_data['District_Id'].values
    
    dist_id=data['District_Id'].values

    for d in dist_id:

        v=data[data['District_Id']==d]['Confirmed']
        
        if prev_end_day<0:
            ans=v.values[0]
        
        else:
            if d in old_dist_id:
                v1,v2=prev_data[prev_data['District_Id']==d]['Confirmed'].values[0],v.values[0]
                ans=v2-v1
            else:
                ans=v.values[0]
            
        weekly_cases.append((d,i+1,ans))

#Replacing State Name with State Code for final outputs
def save_weekly_cases():
    p=['Andaman and Nicobar Islands','Goa','Telangana']

    with open('cases-week.csv','w') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['DistrictId','WeekId','Cases'])
        for row in weekly_cases:
            temp=row[0].partition("_")
            if temp[0] in p:
                key=state_key_mapping[temp[0]]+"_"+temp[0]
            else:
                key=state_key_mapping[temp[0]]+"_"+temp[2]
            csv_out.writerow((key,row[1],row[2]))

save_weekly_cases()


