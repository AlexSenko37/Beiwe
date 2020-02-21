#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 14:35:58 2020
This script looks through patients voice recordings and matches them with
corresponding pain scores. The purpose is to be able to train a neural net to
predict the pain score from the voice recording.
@author: alex
"""

import glob, csv, os, shutil
from datetime import datetime

# path to list of folders containing patient data, where each folder is a patient id
folder_path = "DIRECTORY"

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
def voice_and_pain(patient_id):
    # open file and read into memory
    path, pain_path, hr_pathname = setup_paths(folder_path, patient_id)
        
    # for each voice file for this patient
    for filename in glob.glob(path):    
        #look for a corresponding pain score
        #for each pain survey from this patient
        
        for pain_filename in glob.glob(pain_path):
            
            # check if it was recorded close to voice recording
            voicetime, paintime, thresh = time_between_filenames(filename, pain_filename)
            if thresh:
                
                # if it is, write to csv file and move .mp4 file
                # prepare this row of data
                row = [voicetime.strftime("%Y-%m-%d %H:%M:%S"), paintime.strftime("%Y-%m-%d %H:%M:%S"), get_pain_score_from_file(pain_filename)]
                
                 # start writing the data
                hr_filename = hr_pathname + 'marked_voice_samples.csv'
                if os.path.exists(hr_filename):
                    # check if file with this name (including the date) already exists
                    # if the file already exists, just append more rows of data
                    with open(hr_filename,'a') as csvfile:
                        csvwriter = csv.writer(csvfile)
                        csvwriter.writerow(row)
                else:
                    # if not, make a new file, and include headers
                    with open(hr_filename,'w') as csvfile:
                        csvwriter = csv.writer(csvfile)
                        csvwriter.writerow(['voice recording time','pain survey time','pain score'])
                        csvwriter.writerow(row)    
        
                # copy .mp4 file to folder
                source = filename
                destination = hr_pathname + filename[-23:]
                shutil.copyfile(source, destination) 

# returns true if two files were recorded within 3 hours of each other
def time_between_filenames(filename1, filename2, diff_threshold = 10800):
    # times are contained in names of files
    # strip filenames of underscores and dashes and spaces
    filename1 = get_timestamp_from_filename(filename1)
    filename2 = get_timestamp_from_filename(filename2)
    # threshold for "close enough" in time is 3 hours (10800 seconds)
    time1 = datetime.strptime(filename1, '%Y%m%d%H%M%S')
    time2 = datetime.strptime(filename2, '%Y%m%d%H%M%S')
    time_diff = (time1 - time2).total_seconds()
    within_thresh = abs(time_diff) < diff_threshold
    #print(time_diff,within_thresh)
    return time1, time2, within_thresh

def get_pain_score_from_file(filename):
    with open(filename, 'r') as f:
        # read the short file into one string
        text = f.read()
        # find the text before the patient's score is recorded
        ind = text.find('= 10,')
        # the patient's score is the one or two chars after that string
        score_char = text[ind+5]
        if score_char != 'N':
            if text[ind+6] == '0':
                return 10
                #pain_scores.append(pain_lvl)
            else:
                return int(score_char)
                #pain_scores.append(pain_lvl)
        else:
            return None

def get_timestamp_from_filename(filename):
    cur_file = filename[-23:-4]
    cur_file = cur_file.replace('_','')
    cur_file = cur_file.replace('-','')
    cur_file = cur_file.replace(' ','')
    return cur_file

def setup_paths(folder_path, patient_id):
    path = folder_path + patient_id + "/" + patient_id + "/audio_recordings/5707acc11206f77d6167a946/*.mp4"  
    
    # check format of storage
    if os.path.isdir(os.path.dirname(path)) == False:
        path = folder_path + patient_id + "/" + patient_id + "/audio_recordings/*.mp4"  
    
    # create path to store patient files
    hr_pathname = write_path + patient_id + '/audio_recordings/'
    if os.path.isdir(os.path.dirname(os.path.dirname(hr_pathname))) == False:
        os.mkdir(os.path.dirname(os.path.dirname(hr_pathname)))
    # create path to store patient gps daily files
    if os.path.isdir(hr_pathname) == False:
        os.mkdir(hr_pathname)
        
    pain_path = folder_path + patient_id + "/" + patient_id + "/survey_answers/56d60b801206f7036f8919ee/*.csv"  
    
    return path, pain_path, hr_pathname

# execute functions here to collect voice data
patient_ids = get_ids(folder_path)
for id in patient_ids:
    voice_and_pain(id)
