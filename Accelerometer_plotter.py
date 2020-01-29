# -*- coding: utf-8 -*-
"""
This script plots an hour of accelerometer data from a patient's smartphone
"""
import numpy as np
import glob, csv
from math import sqrt as sqrt
import matplotlib.pyplot as plt

# open file and read into memory
path = "DIRECTORY/*.csv"

files = glob.glob(path)
    
# initializing the titles and rows list 
fields = [] 
rows = [] 
  
# reading csv file 
with open(files[6],'r') as csvfile: 
    # creating a csv reader object 
    csvreader = csv.reader(csvfile)
    # extracting field names through first row 
    fields = next(csvreader) 
    # extracting each data row one by one 
    for row in csvreader: 
        rows.append(row)

# extract timestamp, x, y, z to matrix
accel = []        
for row in rows:
    ap = [row[0], row[3], row[4], row[5]]
    ap = [float(i) for i in ap]
    # add magnitude calculation
    ap.append(sqrt(ap[1] ** 2 + ap[2] ** 2 + ap[3] ** 2))
    accel.append(ap)

#convert to numpy array
accel_np = np.array(accel)

# plot data
t = accel_np[:,0]
a = accel_np[:,4]
fig, ax = plt.subplots()
ax.plot(t, a)
ax.set(xlabel='time (ms)', ylabel='acceleration (g)',
       title='Accelerometer data')
ax.grid()
fig.savefig("Accelerometer.png")
plt.show()
