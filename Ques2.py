# Importing libraries 

import json
import csv
import warnings 
warnings.filterwarnings('ignore')

# Fetching neighbor-districts-modified.json of question 1

f=open("neighbor-districts-modified.json")   #json file
neighbor_districts_modified=json.load(f)


fields=["District 1","District 2"]                   # Column Names in required edge-graph.csv file

rows=[] 

for item in neighbor_districts_modified:
    for n in neighbor_districts_modified[item]:
        rows.append([item,n])

with open("edge-graph.csv", 'w') as csvfile:   #edge-graph.csv
    csvwriter = csv.writer(csvfile) 
    csvwriter.writerow(fields) 
    csvwriter.writerows(rows)
    

