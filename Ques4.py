# Importing libraries 

import json
import csv
import requests
import pandas as pd
import numpy as np
import datetime
from pprint import pprint
from math import isnan
from scipy.signal import find_peaks

import warnings 
warnings.filterwarnings('ignore')

# state code mapping - Maps state name with state code

def state_Id_Mapping():
    df=pd.read_csv('cowin_vaccine_data_districtwise.csv')
    df=df[["State","State_Code"]].dropna()
    d=pd.Series(df.State_Code.values,index=df.State).to_dict()
    return d

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

# districts.csv contains data from 26-04-2020 to 02-09-2021
# Filter out Data between 26-04-2020 - 14-08-2021

df=pd.read_csv('districts.csv')
#df=df[["Date","State","District","Confirmed"]]
df['Date']=pd.to_datetime(df['Date'])

end_date='14-08-2021'
mask=(df['Date'] <= end_date)

df=df.loc[mask]

df['District_Id']=df['State']+"_"+df['District']

df['Active Cases']=df['Confirmed']-df['Recovered']-df['Deceased']

monthly_cases=[]  #To store monthly cases in the form of tuple-(DistrictID,WeekID,Number of cases)

# Function to calculate number of active cases per month

def active_cases_monthly():

    month_end=['2020-05-14', '2020-06-14', '2020-07-14', '2020-08-14', '2020-09-14', '2020-10-14', '2020-11-14','2020-12-14', 
           '2021-01-14', '2021-02-14', '2021-03-14', '2021-04-14', '2021-05-14', '2021-06-14', '2021-07-14','2021-08-14']

    for i in range(len(month_end)):    
        end_day=i
        end_data=df[(df['Date']==str(month_end[end_day]))]
        end_dist_id=end_data['District_Id'].values

        for d in end_dist_id:
            active_cases=end_data[end_data['District_Id']==d]['Active Cases'].values[0]      
            monthly_cases.append((d,i+1,active_cases))

active_cases_monthly()

dist_monthly={} # dictionary to store monthly cases {key=districtID,value=list containing number of active cases corresponding to that districtID}

for item in monthly_cases:
    dist_monthly[item[0]]=[0]*16

for item in monthly_cases:
    dist_monthly[item[0]][item[1]-1]=item[2]

# function to find month having peaks for wave 1 and wave 2

def find_peak_month(x):
    peaks,_ = find_peaks(x)

    m1,peak_month_wave1=-1,-1
    m2,peak_month_wave2=-1,-1

    for item in peaks:
        if item <=8:
            if m1<x[item]:
                m1=x[item]
                peak_month_wave1=item
        else:
            if m2<x[item]:
                m2=x[item]
                peak_month_wave2=item
    
    return [peak_month_wave1,peak_month_wave2] # It return index of peak,so to get month id we need to do +1

weekly_cases=[]  #To store weekly cases in the form of tuple-(DistrictID,WeekID,Number of cases)

def active_cases_weekly():
    dates=date_generator()
    
    no_of_weeks=len(dates)//7
    
    c1,c2=1,2
    
    # Calculating number of active cases per week (week starts from sunday and ends on saturday)
    
    for i in range(no_of_weeks):
        end_day=i*7+6
        data=df[df['Date']==str(dates[end_day])]
        dist_id=data['District_Id'].values
        
        for d in dist_id:
            active_cases=data[data['District_Id']==d]['Active Cases'].values[0]
            weekly_cases.append((d,c1,active_cases))
        c1+=2
        
    dates=dates[4:]
    
    # Calculating number of active cases per week (week starts from thrusday and ends on wednesday)
    
    for j in range(0,no_of_weeks):
        end_day=j*7+6
        
        if (j==no_of_weeks-1):
            end_day=-1
            
        data=df[df['Date']==str(dates[end_day])]
        
        for d in dist_id:
            active_cases=data[data['District_Id']==d]['Active Cases'].values
            for item in active_cases:
                v=item
                
            weekly_cases.append((d,c2,v))
        c2+=2

# Sort weekly cases on the basis of weekid

weekly_cases.sort(key=lambda x:x[1])

active_cases_weekly()

# p stores state_id_mapping
p=state_Id_Mapping()

dist_weekly={}    # dictionary to store weekly cases {key=districtID,value=list containing number of active cases corresponding to that districtID}

for item in weekly_cases:
    dist_weekly[item[0]]=[0]*136    # initialization with 0

for item in weekly_cases:
    dist_weekly[item[0]][item[1]-1]=item[2]

# function to find week having peaks for wave 1 and wave 2

def find_peak_week(x):
    peaks,_ = find_peaks(x)

    m1,peak_week_wave1=-1,-1
    m2,peak_week_wave2=-1,-1

    for item in peaks:
        if item <=80:
            if m1<x[item]:
                m1=x[item]
                peak_week_wave1=item
        else:
            if m2<x[item]:
                m2=x[item]
                peak_week_wave2=item
    
    return [peak_week_wave1,peak_week_wave2] # It return index of peak,so to get week id we need to do +1

dist_peak={}  # Dictionary to store districtwise peaks 
  
for item in dist_weekly:
    temp=find_peak_week(dist_weekly[item])
    part=item.partition("_")
    val=p[part[0]]+"_"+part[2]    
    temp[0]+=1                                # adding 1 bcz indexing starts from 0 and weekid from 1
    temp[1]+=1                                # adding 1 bcz indexing starts from 0 and weekid from 1

    if (temp[0]==0):
        temp[0]="N/A"
    
    if (temp[1]==0):
        temp[1]="N/A"

    dist_peak[item]=[val,temp[0],temp[1]]

for item in dist_monthly:
    temp=find_peak_month(dist_monthly[item])
    part=item.partition("_")
    val=p[part[0]]+"_"+part[2]
    temp[0]+=1                                #adding 1 bcz indexing starts from 0 and monthid from 1
    temp[1]+=1                                #adding 1 bcz indexing starts from 0 and monthid from 1

    if (temp[0]==0):
        temp[0]="N/A"
    
    if (temp[1]==0):
        temp[1]="N/A"

    if item in dist_peak:
        dist_peak[item].extend([temp[0],temp[1]])

statewise_distname={}

for item in dist_weekly:
    temp=item.partition("_")
    if temp[0] in statewise_distname:
        statewise_distname[temp[0]].append(item)
    else:
        statewise_distname[temp[0]]=[item]

state_weekly={}
for st in statewise_distname:
    l=[]
    for item in statewise_distname[st]:
        l.append(dist_weekly[item])
    temp1=[sum(i) for i in zip(*l)]
    state_weekly[p[st]]=temp1

state_peak={}
for item in state_weekly:
    temp=find_peak_week(state_weekly[item])
    temp[0]+=1                                # adding 1 bcz indexing starts from 0 and weekid from 1
    temp[1]+=1                                # adding 1 bcz indexing starts from 0 and weekid from 1

    if (temp[0]==0):
        temp[0]="N/A"
    
    if (temp[1]==0):
        temp[1]="N/A"
    state_peak[item]=[item,temp[0],temp[1]]

dist_in_state={}

for item in dist_monthly:
    temp=item.partition("_")
    if temp[0] in dist_in_state:
        dist_in_state[temp[0]].append(item)
    else:
        dist_in_state[temp[0]]=[item]

state_monthly={}
for st in dist_in_state:
    l=[]
    for item in dist_in_state[st]:
        l.append(dist_monthly[item])
    temp1=[sum(i) for i in zip(*l)]
    state_monthly[p[st]]=temp1

for item in state_monthly:
    temp=find_peak_month(state_monthly[item])
    temp[0]+=1                                #adding 1 bcz indexing starts from 0 and monthid from 1
    temp[1]+=1                                #adding 1 bcz indexing starts from 0 and monthid from 1

    if (temp[0]==0):
        temp[0]="N/A"
    
    if (temp[1]==0):
        temp[1]="N/A"
        
    if item in state_peak:
        state_peak[item].extend([temp[0],temp[1]])

overall_weekly={}
l2=[]
for st in state_weekly:
    l2.append(state_weekly[st])
temp2=[sum(i) for i in zip(*l2)]
overall_weekly['India']=temp2

overall_monthly={}
l3=[]
for st in state_monthly:
    l3.append(state_monthly[st])
temp3=[sum(i) for i in zip(*l3)]
overall_monthly['India']=temp3

overall_peak=[]
temp4=find_peak_week(overall_weekly['India'])
overall_peak.extend(["India",temp4[0]+1,temp4[1]+1])

temp5=find_peak_month(overall_monthly['India'])
overall_peak.extend([temp5[0]+1,temp5[1]+1])

# Function to Save districtwise peaks

def save_dist_peaks():
    discard=["HR_Italians","HR_Unknown","AS_Dibrugarh","ML_Unknown","KA_Other State","RJ_Evacuees","RJ_Italians","RJ_Other State","AP_Other State","RJ_BSF Camp","WB_Other State","GJ_Other State","TN_Other State","CT_Unknown","TN_Railway Quarantine","TR_Unknown","AP_Foreign Evacuees","HR_Foreign Evacuees","UT_Unknown","AR_Capital Complex","NL_Unknown","AS_Udalguri","MN_Churachandpur","MP_Unknown"]
    with open('district-peaks.csv','w') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['DistrictId','Wave1-WeekId','Wave2-WeekId','Wave1-MonthId','Wave2-MonthId'])
        for row in dist_peak:
            l=dist_peak[row]
            if (len(dist_peak[row]))==5:
                if l[0] in discard:
                    pass
                else:
                    csv_out.writerow((l[0],l[1],l[2],l[3],l[4]))

save_dist_peaks()

# Function to Save statewise peaks
def save_state_peaks():
    with open('state-peaks.csv','w') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['StateId','Wave1-WeekId','Wave2-WeekId','Wave1-MonthId','Wave2-MonthId'])
        for row in state_peak:
            l=state_peak[row]
            if (len(state_peak[row]))==5:
                csv_out.writerow((l[0],l[1],l[2],l[3],l[4]))

save_state_peaks()

# Function to Save overall peaks
def save_overall_peaks():
    with open('overall-peaks.csv','w') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(['CountryId','Wave1-WeekId','Wave2-WeekId','Wave1-MonthId','Wave2-MonthId'])
        csv_out.writerow(overall_peak)

save_overall_peaks()

