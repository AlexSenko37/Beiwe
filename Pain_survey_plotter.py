# -*- coding: utf-8 -*-
"""
This script combines .csv files for patient responses to the Beiwe pain survey
It saves one .csv file per patient, where each row contains a score and the name
of the file that the score came from.
It also plots the data.
"""

import glob, csv, os
import matplotlib.pyplot as plt

# path to list of folders containing patient data, where each folder is a patient id
folder_path = "DIRECTORY CONTAINING DIRECTORIES OF PATIENTS"

# create directory to store processed files and plots
write_path = os.path.join(os.path.dirname(os.path.dirname(folder_path)),'Analysis/')
if os.path.isdir(write_path) == False:
    os.mkdir(write_path)

# get list of folder names (patient ids)
def get_ids(folder_path):
    # just take the last part of the path to get the patient ids
    # some patients only have a 7 digit id. In that case, strip the preceeding '/'
    return [foldername[-8:].strip('/') for foldername in glob.glob(folder_path + '*')]

# generate a list of pain scores, one score per .csv file    
def get_pain_scores(patient_id):
    # open file and read into memory
    path = folder_path + patient_id + "/" + patient_id + "/survey_answers/56d60b801206f7036f8919ee/*.csv"  
    pain_scores = []
    file_names = []
    # for all files in this folder containing survey responses
    for filename in glob.glob(path):
        with open(filename, 'r') as f:
            # read the short file into one string
            text = f.read()
            # find the text before the patient's score is recorded
            ind = text.find('= 10,')
            # the patient's score is the one or two chars after that string
            score_char = text[ind+5]
            if score_char != 'N':
                if text[ind+6] == '0':
                    pain_lvl = 10
                    pain_scores.append(pain_lvl)
                else:
                    pain_lvl = int(score_char)
                    pain_scores.append(pain_lvl)
        # convert 'filename' (a path) to just the name of the .csv file
        file_names.append(filename[-23:-4])
        #write .csv file with all pain scores
        with open(write_path + patient_id + '_pain_scores.csv','w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['filename','pain_score'])
            csvwriter.writerows(zip(file_names,pain_scores))
    return pain_scores

# plot the collected pain scores        
def plot_pain(pain_scores,patient_id):        
    fig, ax = plt.subplots()
    ax.plot(pain_scores)
    ax.set(xlabel='Day', ylabel='Pain level',title='Daily pain level')
    ax.grid()
    ax.set_ylim([0,10])
    # save fig to working directory   
    fig.savefig(write_path + "Pain_" + patient_id + ".png")
    # show fig in console
    plt.show()

# execute functions here to collect and plot pain data
patient_ids = get_ids(folder_path)
for id in patient_ids:
    ps = get_pain_scores(id)
    if ps:
        plot_pain(ps,id)
