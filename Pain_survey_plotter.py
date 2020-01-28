# -*- coding: utf-8 -*-
"""
This script combines .csv files for patient responses to the pain survey
"""
import numpy as np
import glob
import csv
from math import sqrt as sqrt
import matplotlib.pyplot as plt

# open file and read into memory
patient_id = 'bvg4zvna'
path = "/Users/alex/Desktop/DP Pituitary Data (Asad)/" + patient_id + "/" + patient_id + "/survey_answers/56d60b801206f7036f8919ee/*.csv"

pain_scores = []
#files = glob.glob(path)
for filename in glob.glob(path):
    with open(filename, 'r') as f:
        text = f.read()
        ind = text.find('= 10,')
        score_char = text[ind+5]
        if score_char != 'N':
            pain_lvl = int(text[ind+5])
            pain_scores.append(pain_lvl)
            
            
        
            

#with open(files[0],'r') as f:
    
## initializing the titles and rows list 
#fields = [] 
#rows = [] 
#  
## reading csv file 
#with open(files[5],'r') as csvfile: 
#    # creating a csv reader object 
#    csvreader = csv.reader(csvfile) 
#      
#    # extracting field names through first row 
#    fields = next(csvreader) 
#  
#    # extracting each data row one by one 
#    for row in csvreader: 
#        rows.append(row)

## extract timestamp, x, y, z to matrix
#accel = []        
#for row in rows:
#    ap = [row[0], row[3], row[4], row[5]]
#    ap = [float(i) for i in ap]
#    # add magnitude calculation
#    ap.append(sqrt(ap[1] ** 2 + ap[2] ** 2 + ap[3] ** 2))
#    accel.append(ap)
#    
#accel_np = np.array(accel)
#
# plot data
#t = accel_np[:,0]
#a = accel_np[:,4]
fig, ax = plt.subplots()
ax.plot(pain_scores)

ax.set(xlabel='Day', ylabel='Pain level',
       title='Daily pain level')
ax.grid()

fig.savefig("Pain_" + patient_id + ".png")
plt.show()

