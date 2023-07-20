# -*- coding: utf-8 -*-
"""
THIS IS STILL BAD CODE.
BUT IT IS LESS BAD THAN BEFORE.

oct 12 2022

@author: mauspad
"""
# import packages
import pandas as pd
import numpy
import ast
import os
import re
import shutil

# constants
PATH = os.getcwd()
OUT_DIR = "scored"
OUT_TEMPLATE= "baseline_milkshake_"
OUT_PRE = "clear all;\n\nnames=cell(1,3);\nonsets=cell(1,3);\ndurations=cell(1,3);\n\nnames{1}=\'milk\';\nnames{2}=\'tless\';\nnames{3}=\'rinse\';\n\n"
OUT_END = "\ndurations{1}=[4];\ndurations{2}=[4];\ndurations{3}=[0];\n\n"

def stringify_onsets(lst):
    lst = [str(x) for x  in lst]
    return ", ".join(lst)

def score_subject(subjID, in_file):
    # turn csv into dataframe
    df = pd.read_csv("data/" + in_file) #change!

    # set up some variables
    trialno = list(range(0,60)) # trial number

    # calculate and list task onsets relative to scanner start
    real_start_1 = df.at[0, "trigger.rt"]
    real_start_2 = df.at[0, "trigger.started"]
    real_start = real_start_1 + real_start_2
    taste_onset_raw = df["taste_delivery_ITI.started"].tolist()
    del taste_onset_raw[0]
    taste_onset = numpy.array(taste_onset_raw)
    taste_onset = (taste_onset - real_start).tolist()
    rinse_onset_raw = df["rinse_ITI_fixation.started"].tolist()
    del rinse_onset_raw[0]
    rinse_onset = numpy.array(rinse_onset_raw)
    rinse_onset = (rinse_onset - real_start).tolist()
    eventtype = df["eventtype"].tolist()
    del eventtype[0]

    # make some empty lists to sort into
    milkonset = []
    tlessonset = []
    rinseonset = []

    # loop!
    for i in trialno:
        if eventtype[i] == "tless":
            tlessonset.append(taste_onset[i])
        elif eventtype[i] == "milkstraw" or eventtype[i] == "milkchoc":
            milkonset.append(taste_onset[i])
            rinseonset.append(rinse_onset[i])

    milkonset = [round(i,2) for i in milkonset]
    tlessonset = [round(i,2) for i in tlessonset]
    rinseonset = [round(i,2) for i in rinseonset]

    # print("Milk: " + str(milkonset) + "\n")
    # print("Tasteless: " + str(tlessonset) + "\n")
    # print("Rinse: " + str(rinseonset) + "\n")

    return (milkonset, tlessonset, rinseonset)

if __name__ == "__main__":
    # make output folder if not already present
    try:
        os.mkdir(OUT_DIR)
    except:
        pass
    # get all files in /data
    all_data = os.listdir(PATH + "/data")
    # filter for subject .csv
    all_data = [f for f in all_data if re.search("^[12][0-9][0-9][0-9].*\.csv$", f)]
    for raw in all_data:
        subjID = raw[0:4]
        print(subjID)

        # skipping subject 2625
        if "2625" in subjID:
            continue

        output = score_subject(subjID, raw)
        outfile_name = OUT_TEMPLATE + subjID + ".m"
        out = open(outfile_name, "w")
        out.write(OUT_PRE)
        for i in range(len(output)):
            out.write("onsets{" + str(i + 1) + "}=[" + stringify_onsets(output[i]) + "];\n")
        out.write(OUT_END)
        out.write("save(\'" + outfile_name + "at\','names','onsets','durations')")
        try:
            shutil.move(outfile_name, OUT_DIR)
        except shutil.Error as err:
            print("ERROR: " + subjID)
            pass
        out.close()



