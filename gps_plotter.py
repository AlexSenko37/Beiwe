# -*- coding: utf-8 -*-
"""
This script plots an hour of accelerometer data from a patient's smartphone
"""
import numpy as np
import glob, csv, random
import matplotlib.pyplot as plt

# open file and read into memory
path = "/DIRECTORY/PATIENT_ID/gps/*.csv"

files = glob.glob(path)
    
# initializing figure  
fig, ax = plt.subplots()

# for each day
for file in files: 
    rows = []
    # reading csv file 
    with open(file,'r') as csvfile: 
        # creating a csv reader object 
        csvreader = csv.reader(csvfile)
        # extracting field names through first row 
        _ = next(csvreader) 
        # extracting each data row one by one 
        for row in csvreader: 
            rows.append(row)
    
    # extract timestamp, x, y, z to matrix
    accel = []        
    for row in rows:
        ap = [row[0], row[2], row[3], row[4]]
        ap = [float(i) for i in ap]
        accel.append(ap)
    
    #convert to numpy array
    accel_np = np.array(accel)
    
    # plot data
    long = accel_np[:,2]
    lat = accel_np[:,1]
    plt.plot(long, lat, marker='o', color = [random.random(), random.random(), random.random()])

#show plot
ax.set(xlabel='longitude', ylabel='lattidude',
   title='GPS location')
ax.grid()
plt.show()
fig.savefig("gps_sample.png")
