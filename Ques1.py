# Importing libraries 

import json
import csv
import requests
import pandas as pd
import numpy as np
import warnings 
warnings.filterwarnings('ignore')

# Fetching vaccination data from 'cowin_vaccine_data_districtwise.csv' available on https://data.covid19india.org/

df=pd.read_csv('cowin_vaccine_data_districtwise.csv')
df=df[["State_Code",	"State",	"District_Key",	"District"]]
vaccine_data=df.to_dict("records")
#pprint(vaccine_data)
#print(len(vaccine_data))


# Fetching covid data from covid portal (https://data.covid19india.org/)

url="https://data.covid19india.org/v4/min/data.min.json"
r=requests.get(url)
covid19_data=r.json()

s={}    # Dictionary having state name as a key and list of its districts as a value

total_district_count=0

for state in covid19_data:
    dist=[]
    for item in covid19_data[state]:
        if 'districts' in item:
            for d in covid19_data[state]['districts']:
                dist.append(d)
                total_district_count+=1
    s[state]=dist
#pprint(s)
#print("Total District- ",total_district_count)

# Checking whether districts present in vaccine_data also present in s or not 

yes=no=0
for i in range(len(vaccine_data)):
    temp=vaccine_data[i]['District']
    for item in s:
        if(item==vaccine_data[i]['State_Code']):
            if temp in s[item]:
                yes+=1
            else:
                no+=1
                #print(temp)     priniting unmathced districts from s(covid data)
#print(yes,no)    yes=743  no=11

# All the 11 unmathced districts are from delhi state because in vaccination data delhi state is divided into multiple districts,but in covid data it is considered as a single district.


# Working with given neighbor-districts.json

f=open("neighbor-districts.json")
neighbor_districts=json.load(f)

# Preprocessing for spelling mismatch 

# 'Mistakes.csv' contains incorrect and correct district names of mismatched data

df=pd.read_csv('Mistakes.csv') 

correction=pd.Series(df.Correct.values,index=df.Wrong).to_dict()

# Correction dictionary contains {'incorrect name':'correct name' } key value pair

neighbor_districts_modified={}

dist_key_value={}

for d in neighbor_districts:
    district=d.partition("/")[0]
    district=district.partition("_District")[0]     # Removing _District from the end of district name
    district=district.partition("_district")[0]     # Removing _district from the end of district name
    district=district.replace("_", " ")             # Replacing "_" with whitespace in district name
    district=district.replace("–", " ")             # Replacing "–" with whitespace in district name
    district=district.replace("-", " ")             # Replacing "-" with whitespace in district name
    
    for i in range(len(vaccine_data)):
        if (vaccine_data[i]['District']==district.title()):
            key=d
            dist_key_value[key]=vaccine_data[i]['District_Key']
            
        elif district.title() in correction:
            for i in range(len(vaccine_data)):
                if(vaccine_data[i]['District']==correction[district.title()]):
                    key=d
                    dist_key_value[key]=vaccine_data[i]['District_Key']
                    
#print("dist_key_value=",len(dist_key_value))
#pprint(dist_key_value)

#print(len(neighbor_districts))
#print(len(dist_key_value))
discarded=[]
for d in neighbor_districts:
    if (dist_key_value.get(d)) is None:
        discarded.append(d)

#print(discarded)
#final_dict = {x:neighbor_districts[x] for x in neighbor_districts if x in dist_key_value}

for item in neighbor_districts:
    if item not in discarded:
        key=dist_key_value[item]
        value=[]
        for near in neighbor_districts[item]:
            if near not in discarded:
                value.append(dist_key_value[near])
        neighbor_districts_modified[key]=value

#pprint(neighbor_districts_modified)
#print(len(neighbor_districts_modified))

# Sorting districts

for item in neighbor_districts_modified:
    neighbor_districts_modified[item].sort()

#pprint(neighbor_districts_modified)

#json_object = json.dumps(neighbor_districts_modified,indent = 4)

with open('neighbor-districts-modified.json','w') as json_file:
    json.dump(neighbor_districts_modified,json_file,indent=2,sort_keys=True)


