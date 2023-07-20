import pandas as pd
import csv
import numpy
import ast
import os

# IMPORTANT: need to clean up data folder by removing all .psydat and .log

# Modify the global constants to match the filenames and paths of your own directory/REDCap template
OUTPUT_FILE = 'output.csv'
ANSWER_SHEET = 'trials.xlsx'
START_LABEL = "BlueOri"
GOAL_LABEL = "RedOri"
MOVEMENT_LABEL = "Angle"
DATA_PATH = 'data/'
DEG_OFF_LABEL = 'vsplot_off'
SUBJ_ID_LABEL = 'participant_id'
TIMEPOINT_LABEL = 'redcap_event_name'
TOTAL_CORRECT_LABEL = 'vsplot_tc'
COMPLETE_LABEL = 'cognition_vsplot_complete'

# REDCap upload template fields
FIELDNAMES = ['participant_id', 'redcap_event_name', 'vsplot_tc', 'vsplot_off', 'vsplot_off1', 'vsplot_off2', 'vsplot_off3', 'vsplot_off4', 'vsplot_off5', 'vsplot_off6', 'vsplot_off7', 'vsplot_off8', 'vsplot_off9', 'vsplot_off10', 'vsplot_off11', 'vsplot_off12', 'vsplot_off13', 'vsplot_off14', 'vsplot_off15', 'vsplot_off16', 'vsplot_off17', 'vsplot_off18', 'vsplot_off19', 'vsplot_off20', 'vsplot_off21', 'vsplot_off22', 'vsplot_off23', 'vsplot_off24', 'cognition_vsplot_complete']

def parse_trials():
    """ gets list of starting positions and goal positions from the answer sheet """
    trials = pd.read_excel(ANSWER_SHEET)
    start = trials[START_LABEL].tolist()
    goals = trials[GOAL_LABEL].tolist()
    mvmt = trials[MOVEMENT_LABEL].tolist()
    return start, goals, mvmt

# preprocessing code and prints by @mauspad with minor restructuring and renaming
def analyze_PLOT(filename, start, goal, mvmt):
    # create variable to store subject results
    subj_results = dict()

    subj_results[SUBJ_ID_LABEL] = filename[0:4]

    # get user input
    user_in = pd.read_csv(DATA_PATH + filename)

    # loop through all trials to count num correct, degrees off, reaction times, etc.
    num_correct = 0
    trials_deg_off = []
    rt = []

    for i in range(0,24):
        # orientation of line is symmetric
        goal[i] = goal[i] % 180

        # preprocess user input
        key_list = user_in["key_resp.keys"].iloc[i]
        if ('3' in key_list): # detect 3s, make last element, flag if not present
            target = key_list.index('3')
            key_list = key_list[:target]
        else:
            print("Did not lock in trial " + str(i))

        # count 1s and 2s - they are duplicated FSR
        ones = ((key_list.count('1')) // 2)
        twos = ((key_list.count('2')) // 2)

        # calculate degree participant entered
        subj_ans = (start[i] + (mvmt[i] * (twos - ones)))
        subj_ans %= 180

        # catch trial 7 error
        if i == 6:
            # if difference with goal is 3, count as correct
            if abs(subj_ans - goal[i]) == 3:
                num_correct += 1
                deg_off = 0
                #print("Trial " + str(i + 1) + " correct!")

            # else calculate degrees off from either side of the goal
            else:
                from_180 = 180 - goal[i]
                deg_off = min(abs(subj_ans - (goal[i] - 3)), abs(subj_ans - (goal[i] + 3)), subj_ans + from_180 - 3)
                #print("Trial " + str(i + 1) + " incorrect; " + str(deg_off) + " degrees off")

            trials_deg_off.append(deg_off)
            continue

        # if degree is goal, count as correct
        if subj_ans == goal[i]:
            num_correct += 1
            deg_off = 0
            #print("Trial " + str(i + 1) + " correct!")
        # o.w. count as incorrect and record degrees off
        else:
            #print(subj_ans)
            from_180 = 180 - goal[i]
            deg_off = min(abs(subj_ans - goal[i]), subj_ans + from_180)
            trials_deg_off.append(deg_off)
            #print("Trial " + str(i + 1) + " incorrect; " + str(deg_off) + " degrees off")

        # the following line may not be correct for all REDCap templates - change
        subj_results[DEG_OFF_LABEL + str((i + 1))] = deg_off

    # sanity check
    #print("Total correct: " + str(num_correct) + " out of 24")
    avgdeg = round(sum(trials_deg_off) / len(trials_deg_off), 2)
    #print("Average degrees off: " + str(avgdeg))

    # store and return subject results
    subj_results[TOTAL_CORRECT_LABEL] = num_correct
    subj_results[DEG_OFF_LABEL] = sum(trials_deg_off)
    subj_results[COMPLETE_LABEL] = "0"
    return subj_results

if __name__ == "__main__":
    with open(OUTPUT_FILE, 'w') as out:
        #object that writes to output csv
        writer = csv.DictWriter(out, fieldnames=FIELDNAMES)
        writer.writeheader()

        # get start and goal angles
        start, goal, mvmt = parse_trials()

        # get list of all data files
        all_data_files = [f for f in os.listdir(DATA_PATH) if '.DS' not in f and '.csv' in f]
        #analyze_PLOT('21002_PLOT_behavioral_2021_Mar_15_1130.csv', start, goal, mvmt)
        #for each participant, compare user input difference with end state and store discrepancy in a dict
        for f in all_data_files:
            try:
                subj_results = analyze_PLOT(f, start, goal, mvmt)
            except:
                print("error in", f)
            writer.writerow(subj_results)
            


            
