# -*- coding: utf-8 -*-
# import packages
import pandas as pd
import csv
import numpy
import ast
import os
import re
import shutil
from collections import defaultdict

# constants
PATH = os.getcwd()
NUM_RUNS = 2
NUM_CONDITIONS = 3
FOODS_PER_CONDITION = 12
CONDITIONS = ['carb', 'combo', 'fat']
COVARIATES = ['estimated calories', 'actual energy density', 'liking', 'estimated price', 'bid']
BID_DATA_PATH = "/RQ_bid_data.csv"
DATA_PATH = "/data"
OUT_DIR = "scored"`
OUT_TEMPLATE= "baseline_auction_"
OUT_PRE = "clear all;\n\nnames=cell(1,4);\nonsets=cell(1,4);\ndurations=cell(1,4);\n\nnames{1}=\'carb\';\nnames{2}=\'combo\';\nnames{3}=\'fat\';\nnames{4}=\'auction\';\n\n"
OUT_PRE_MISSED = "clear all;\n\nnames=cell(1,5);\nonsets=cell(1,5);\ndurations=cell(1,5);\n\nnames{1}=\'carb\';\nnames{2}=\'combo\';\nnames{3}=\'fat\';\nnames{4}=\'auction\';\nnames{5}=\'missed\';\n\n"
OUT_END = "\ndurations{1}=[5];\ndurations{2}=[5];\ndurations{3}=[5];\ndurations{4}=[5];\n\north{1}=0;\north{2}=0;\north{3}=0;\north{4}=0;\n\n"
OUT_END_MISSED = "\ndurations{1}=[5];\ndurations{2}=[5];\ndurations{3}=[5];\ndurations{4}=[5];\ndurations{5}=[5];\n\north{1}=0;\north{2}=0;\north{3}=0;\north{4}=0;\north{5}=0;\n\n"

def stringify_onsets(lst):
    lst = [str(x) for x  in lst]
    return ", ".join(lst)

def calculate_true_auction_start(row):
    try:
        return row['fix_pause.started'] + row['jitter']
    except:
        return 'nan'

def score_subject(subjID, in_file):
    # turn csv into dataframe
    df = pd.read_csv( PATH + DATA_PATH + '/' + in_file)
    bid_df = pd.read_csv(PATH + BID_DATA_PATH)

    trigger_rt = df['trigger.rt'][1]
    trigger_started = df['trigger.started'][1]
    trigger_time = trigger_rt + trigger_started

    # sort alphabetically by food type and name (image_file)
    df = df.sort_values(by=['foodtype', 'image_file'])
    bid_df = bid_df.loc[bid_df['Subject'] == int(subjID)]
    bid_df = bid_df.sort_values(by=['FoodType', 'ImageFile'])
    df['true_start'] = df.apply(lambda row: calculate_true_auction_start(row), axis = 1)
    true_starts = df['true_start'][0:36]
    times = df['food_item.started']

    pmods_zipped = zip(bid_df['EstimatedCalories'], bid_df['ActualEnergyDensity'], bid_df['Like'], bid_df['EstimatedPrice'], df['Bid'])
    
    # declare outputs
    onsets = [[],[],[],[]]
    pmods = defaultdict(lambda: defaultdict(lambda: []))
    missed = []


    # check for misses
    for i, bid in enumerate(df['Bid']):
        if bid == 9999.0:
            missed.append(i)

    # populate output with df
    for i, time in enumerate(times):
        if i < 12:
            onsets[0].append(str(time - trigger_time))
        elif i < 24:
            onsets[1].append(str(time - trigger_time))
        elif i < 36:
            onsets[2].append(str(time - trigger_time))

    # create onset list of true starts
    for start in true_starts:
        onsets[3].append(str(float(start) - float(trigger_time)))

    # populate pmods with parametric modulators 
    for i, tup in enumerate(pmods_zipped):
        if i < 12:
            for j, cov in enumerate(COVARIATES):
                pmods['carb'][cov].append(tup[j])
        elif i < 24:
            for j, cov in enumerate(COVARIATES):
                pmods['combo'][cov].append(tup[j])
        elif i < 36:
            for j, cov in enumerate(COVARIATES):
                pmods['fat'][cov].append(tup[j])

    # omit missed bids, move relevant values to 'missed' event
    if missed:
        missed.reverse()
        onsets.append([])
        for miss in missed:
            if miss < 12:
                missed_onset = onsets[0].pop(miss)
                onsets[4].append(missed_onset)
                for cov in COVARIATES:
                    missed_pmod = pmods['carb'][cov].pop(miss)
            elif miss < 24:
                missed_onset = onsets[1].pop(miss % FOODS_PER_CONDITION)
                onsets[4].append(missed_onset)
                for cov in COVARIATES:
                    missed_pmod = pmods['combo'][cov].pop(miss % FOODS_PER_CONDITION)
            elif miss < 36:
                missed_onset = onsets[2].pop(miss % FOODS_PER_CONDITION)
                onsets[4].append(missed_onset)
                for cov in COVARIATES:
                    missed_pmod = pmods['fat'][cov].pop(miss % FOODS_PER_CONDITION)

    return onsets, pmods, True if missed else False

def write_outfile(subjID, onsets, pmods, missed, run_no):
    outfile_name = OUT_TEMPLATE + "run" + run_no + "_" + subjID + ".m"
    out = open(outfile_name, "w")

    # write declarations, names
    if not missed:
        out.write(OUT_PRE)
    else:
        out.write(OUT_PRE_MISSED)

    # write onsets 
    for j in range(len(onsets)):
        out.write("onsets{" + str(j + 1) + "}=[" + stringify_onsets(onsets[j]) + "];\n")

    out.write("\n")

    # write pmods
    for i in range(NUM_CONDITIONS):
        for j in range(len(COVARIATES)):
            out.write("pmod(" + str(i + 1) + ").name{" + str(j + 1) + "}=" + "\'" + COVARIATES[j] + " " + CONDITIONS[i] + "\';\n")
            out.write("pmod(" + str(i + 1) + ").param{" + str(j + 1) + "}=[" + stringify_onsets(pmods[CONDITIONS[i]][COVARIATES[j]]) + "];\n")
            out.write("pmod(" + str(i + 1) + ").poly{" + str(j + 1) + "}=1;\n")

    # write durations, orths
    if not missed:
        out.write(OUT_END)
    else:
        out.write(OUT_END_MISSED)

    # write save command
    out.write("save(\'" + outfile_name + "at\','names','onsets','pmod','durations','orth')")
    try:
        shutil.move(outfile_name, OUT_DIR)
    except shutil.Error as err:
        print("ERROR: " + subjID)
        pass
    out.close()

if __name__ == "__main__":
    # make output folder if not already present
    try:
        os.mkdir(OUT_DIR)
    except:
        pass
    # get all files in /data
    all_data = os.listdir(PATH + DATA_PATH)
    # filter for subject .csv
    all_data = [f for f in all_data if re.search("^[12][0-9][0-9][0-9].*\.csv$", f)]
    data_grouped = defaultdict(lambda: list())
    for f in all_data:
        data_grouped[f[0:4]].append(f)
    for subjID in data_grouped:
        print(subjID)
        # skipping subject 2625
        if "2625" in subjID:
            continue

        # score and write each run
        for i in range(NUM_RUNS):
            data_grouped[subjID].sort()
            filename = data_grouped[subjID][i]
            try:
                onsets, pmods, missed = score_subject(subjID, filename)
            except:
                print("ERR scoring subject: " + subjID)
            write_outfile(subjID, onsets, pmods, missed, str(i + 1))
            



