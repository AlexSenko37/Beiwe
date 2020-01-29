# -*- coding: utf-8 -*-
"""
This script combines .csv files for GPS data from Beiwe
It saves one .csv file per day per patient, where each row contains a score and the name
of the file that the score came from.
Caution: running this when files are complete will result in doubling the length
of each file (just copying original)
"""

import glob, csv, os

# path to list of folders containing patient data, where each folder is a patient id
folder_path = "/Users/alex/Documents/CNOC/DP Pituitary Data (Asad)/"

# create directory to store processed files and plots
write_path = os.path.join(os.path.dirname(os.path.dirname(folder_path)),'aggregated beiwe data/')
if os.path.isdir(write_path) == False:
    os.mkdir(write_path)

# get list of folder names (patient ids)
def get_ids(folder_path):
    # just take the last part of the path to get the patient ids
    # some patients only have a 7 digit id. In that case, strip the preceeding '/'
    return [foldername[-8:].strip('/') for foldername in glob.glob(folder_path + '*')]

# aggregate gps data into csv files, one file per day   
def aggregate_gps_by_day(patient_id):
    # open file and read into memory
    path = folder_path + patient_id + "/" + patient_id + "/gps/*.csv"  
    # for all files in this folder containing survey responses
    for filename in glob.glob(path):
        rows = []
        with open(filename, 'r') as f:
            # creating a csv reader object 
            csvreader = csv.reader(f)
            # extracting field names through first row 
            _ = next(csvreader) 
            # extracting each data row one by one 
            for row in csvreader: 
                rows.append(row)
        # create path to store patient files
        hr_pathname = write_path + patient_id + '/gps/'
        hr_filename = hr_pathname + filename[-23:-13] + '.csv'
        if os.path.isdir(os.path.dirname(os.path.dirname(hr_pathname))) == False:
            os.mkdir(os.path.dirname(os.path.dirname(hr_pathname)))
        # create path to store patient gps daily files
        if os.path.isdir(hr_pathname) == False:
            os.mkdir(hr_pathname)
        # start writing the data
        if os.path.exists(hr_filename):
            # check if file with this name (including the date) already exists
            # if the file already exists, just append more rows of data
            with open(hr_filename,'a') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(rows)
        else:
            # if not, make a new file, and include headers
            with open(hr_filename,'w') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['timestamp','UTC time','latitude','longitude','altitude','accuracy'])
                csvwriter.writerows(rows)      

# execute functions here to collect gps data
patient_ids = get_ids(folder_path)
for id in patient_ids:
    ps = aggregate_gps_by_day(id)
