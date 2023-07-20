import pandas as pd
import csv
import numpy
import ast
import os


# Modify the global constants to match your own data
OUTPUT_FILE = 'tower_output.csv'
DATA_PATH = 'data/'
FIELDNAMES = ['Subject ID', 'total_correct', 'problem_time', 'planning_time', 'solving_time','moves_over_optimal']
OPTIMAL_NUM_MOVES = 46

def analyze_tol(filename):
    # create variable to store subject results
    subj_results = dict()

    subj_results['Subject ID'] = filename[0:4]


    # get user input
    with open(DATA_PATH + filename) as csvfile:
        reader = csv.DictReader(csvfile)

        # initialize flags and other bookkeeping variables
        new_trial = True
        last_num_moves = 0
        last_trial_correct = False
        last_planning_time = 0

        # initialize subj values
        for field in FIELDNAMES[1:]:
            subj_results[field] = 0

        for row in reader:
            # only score test trials
            if 'test' in row['exp_stage']:
                # standard case - update last_num_moves and add to planning time total if new_trial, set new_trial <- False
                if 'to_' in row['trial_id']:
                    last_num_moves = int(row['num_moves_made'])
                    if new_trial:
                        subj_results['planning_time'] += int(row['stim_duration'])
                        last_planning_time = int(row['stim_duration'])
                        new_trial = False
                # feedback case - increment total_correct, set last_trial_correct appropriately, add to problem time, calculate solving time
                elif 'feedback' in row['trial_id']:
                    if 'true' in row['correct']:
                        last_trial_correct = True
                        subj_results['total_correct'] += 1
                    else:
                        last_trial_correct = False
                    subj_results['problem_time'] += int(row['problem_time'])
                    subj_results['solving_time'] += int(row['problem_time']) - last_planning_time

                # advance case - set new_trial <- True, add moves from last trial to running total and reset move counter
                elif 'advance' in row['trial_id']:
                    new_trial = True
                    subj_results['moves_over_optimal'] += min(20, last_num_moves) if last_trial_correct else 20
                    last_num_moves = 0
            # calculate final 'advance' stage
            elif 'end' in row['trial_id']:
                subj_results['moves_over_optimal'] += min(20, last_num_moves) if last_trial_correct else 20
                subj_results['moves_over_optimal'] -= OPTIMAL_NUM_MOVES



    # return subject results
    return subj_results

if __name__ == "__main__":
    with open(OUTPUT_FILE, 'w') as out:
        #object that writes to output csv
        writer = csv.DictWriter(out, fieldnames=FIELDNAMES)
        writer.writeheader()

        # get list of all data files
        all_data_files = [f for f in os.listdir(DATA_PATH) if '.DS' not in f and '.csv' in f]
        #analyze_PLOT('21002_PLOT_behavioral_2021_Mar_15_1130.csv', start, goal, mvmt)
        #for each participant, compare user input difference with end state and store discrepancy in a dict
        for f in all_data_files:
            try:
                subj_results = analyze_tol(f)
            except:
                print("error in", f)
            writer.writerow(subj_results)
            


            
