import pandas as pd
import csv
import numpy
import ast
import os

# IMPORTANT: need to clean up data folder by removing all .psydat and .log

# Modify the global constants to match the filenames and paths of your own directory/REDCap template
OUTPUT_FILE = 'frank_output.csv'
DATA_PATH = 'data/'


# REDCap upload template fields
FIELDNAMES = ['Subject ID', '80_corr', '20_corr']
NUM_TRIALS_80 = 30
NUM_TRIALS_20 = 30

# preprocessing code and prints by @mauspad with minor restructuring and renaming
def analyze_psm(filename):
    # create variable to store subject results
    subj_results = dict()

    subj_results['Subject ID'] = filename[0:4]
    corr_20 = 0
    corr_80 = 0

    # get user input
    with open(DATA_PATH + filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            #print(row['exp_stage'], row['condition'], row['correct'])
            if 'test' in row['exp_stage'] and '80' in row['condition'] and ('true' in row['correct'] or 'TRUE' in row['correct']):
                corr_80 += 1
            if 'test' in row['exp_stage'] and '20' in row['condition'] and ('true' in row['correct'] or 'TRUE' in row['correct']):
                corr_20 += 1

    # return subject results
    subj_results['80_corr'] = corr_80 / NUM_TRIALS_80
    subj_results['20_corr'] = corr_20 / NUM_TRIALS_20
    return subj_results

if __name__ == "__main__":
    with open(OUTPUT_FILE, 'w') as out:
        #object that writes to output csv
        writer = csv.DictWriter(out, fieldnames=FIELDNAMES)
        writer.writeheader()

        # get list of all data files
        all_data_files = [f for f in os.listdir(DATA_PATH) if '.DS' not in f]
        #analyze_PLOT('21002_PLOT_behavioral_2021_Mar_15_1130.csv', start, goal, mvmt)
        #for each participant, compare user input difference with end state and store discrepancy in a dict
        for f in all_data_files:
            #try:
            subj_results = analyze_psm(f)
            #except:
                #print("error in", f)
            writer.writerow(subj_results)
            


            
