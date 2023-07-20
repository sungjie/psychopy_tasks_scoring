import os
import csv
import pandas as pd
from collections import defaultdict
import shutil

def fat_sugar_score(preference_ratings, randomization_file, subj_id):
	# read in preference_randomization file
	df = pd.read_excel(randomization_file, header=None)
	counters = dict()
	tray_order = list()
	tray_order_unlabeled = list()
	for i in range(2):
		counters["0"] = 1
		counters["low"] = 1
		counters["medium"] = 1
		counters["high"] = 1
		for j in range(12):
			val = str(df.iloc[22 + j].iloc[17 + i])
			tray_order.append(df.iloc[21].iloc[17 + i] + "_" + val + "_" + str(counters[val]))
			tray_order_unlabeled.append(df.iloc[21].iloc[17 + i] + "_" + val)
			counters[val] += 1

	
			

	# create dictionary for results (one row in output)
	results = defaultdict(lambda: 0.0)
	results['subj_id'] = subj_id
	tray_order_unlabeled_set = set()

	# read in fat_sugar_preference file
	tray_counter = 0
	with open(preference_ratings) as f:
		reader = csv.DictReader(f)
		row_counter = 0
		state_ratings = ["hungry", "full", "thirsty", "anxious", "pee"]
		quality_ratings = ["error", "want", "familiar", "creamy", "fatty"]
		for row in reader:
			cup_stage = (row_counter - 4) % 5 if row_counter < 65 else (row_counter - 5) % 5
			if row_counter < 5:
				results["pre_" + state_ratings[row_counter]] = row["ISval"]
			elif row_counter < 125 and cup_stage != 0:
				if row["Intense"]:
					results[tray_order[tray_counter] + "_intense"] = row["Intense"]
					results[tray_order[tray_counter] + "_sweet"] = row["Sweet"]
					results[tray_order[tray_counter] + "_like"] = row["Like"]

					results[tray_order_unlabeled[tray_counter] + "_intense"] += float(row["Intense"])
					results[tray_order_unlabeled[tray_counter] + "_sweet"] += float(row["Sweet"])
					results[tray_order_unlabeled[tray_counter] + "_like"] += float(row["Like"])

					tray_order_unlabeled_set.add(tray_order_unlabeled[tray_counter] + "_intense")
					tray_order_unlabeled_set.add(tray_order_unlabeled[tray_counter] + "_sweet")
					tray_order_unlabeled_set.add(tray_order_unlabeled[tray_counter] + "_like")

				results[tray_order[tray_counter] + "_" + quality_ratings[cup_stage]] = row["VAS"]
				results[tray_order_unlabeled[tray_counter] + "_" + quality_ratings[cup_stage]] += float(row["VAS"])
				tray_order_unlabeled_set.add(tray_order_unlabeled[tray_counter] + "_" + quality_ratings[cup_stage])
			elif row_counter != 65 and row_counter < 125 and cup_stage == 0:
				tray_counter += 1
			elif row_counter > 126 and row_counter < 132:
				results["post_" + state_ratings[row_counter - 127]] = row["ISval"]
			row_counter += 1

	for total in tray_order_unlabeled_set:
		results[total] = round(results[total] / 3.0, 1)

	return results

if __name__ == "__main__":
	RANDS = "randomization_files/"
	OUTFILE = "fat_sugar_preference_scored.csv"

	# create a separate folder for randomization files
	if not os.path.exists("./" + RANDS):
		os.mkdir(RANDS)

	# move randomization files to their own folder
	rands = set()
	subjects_without_randomization_file = set()
	for root, dirs, files in os.walk("./data"):
		for file in files:
			if "randomization" in file:
				dest = "./" + RANDS + file
				os.rename("./data/" + file, dest)
				rands.add(file)
			elif ".psydat" in file:
				os.remove("./data/" + file)

	# set up os.walk for subjects, including a catch if the randomization file is unavailable
	with open(OUTFILE, "w") as f:
		fieldnames = ['subj_id', 'Jello_0_intense', 'Jello_0_sweet', 'Jello_0_like', 'Jello_0_want', 'Jello_0_familiar', 'Jello_0_creamy', 'Jello_0_fatty', 'Jello_low_intense', 'Jello_low_sweet', 'Jello_low_like', 'Jello_low_want', 'Jello_low_familiar', 'Jello_low_creamy', 'Jello_low_fatty', 'Jello_medium_intense', 'Jello_medium_sweet', 'Jello_medium_like', 'Jello_medium_want', 'Jello_medium_familiar', 'Jello_medium_creamy', 'Jello_medium_fatty', 'Jello_high_intense', 'Jello_high_sweet', 'Jello_high_like', 'Jello_high_want', 'Jello_high_familiar', 'Jello_high_creamy', 'Jello_high_fatty', 'Pudding_0_intense', 'Pudding_0_sweet', 'Pudding_0_like', 'Pudding_0_want', 'Pudding_0_familiar', 'Pudding_0_creamy', 'Pudding_0_fatty', 'Pudding_low_intense', 'Pudding_low_sweet', 'Pudding_low_like', 'Pudding_low_want', 'Pudding_low_familiar', 'Pudding_low_creamy', 'Pudding_low_fatty', 'Pudding_medium_intense', 'Pudding_medium_sweet', 'Pudding_medium_like', 'Pudding_medium_want', 'Pudding_medium_familiar', 'Pudding_medium_creamy', 'Pudding_medium_fatty', 'Pudding_high_intense', 'Pudding_high_sweet', 'Pudding_high_like', 'Pudding_high_want', 'Pudding_high_familiar', 'Pudding_high_creamy', 'Pudding_high_fatty', 'pre_hungry', 'pre_full', 'pre_thirsty', 'pre_anxious', 'pre_pee', 'Jello_low_1_intense', 'Jello_low_1_sweet', 'Jello_low_1_like', 'Jello_low_1_want', 'Jello_low_1_familiar', 'Jello_low_1_creamy', 'Jello_low_1_fatty', 'Jello_0_1_intense', 'Jello_0_1_sweet', 'Jello_0_1_like', 'Jello_0_1_want', 'Jello_0_1_familiar', 'Jello_0_1_creamy', 'Jello_0_1_fatty',  'Jello_high_1_intense', 'Jello_high_1_sweet', 'Jello_high_1_like', 'Jello_high_1_want', 'Jello_high_1_familiar', 'Jello_high_1_creamy', 'Jello_high_1_fatty', 'Jello_0_2_intense', 'Jello_0_2_sweet', 'Jello_0_2_like', 'Jello_0_2_want', 'Jello_0_2_familiar', 'Jello_0_2_creamy', 'Jello_0_2_fatty', 'Jello_medium_1_intense', 'Jello_medium_1_sweet', 'Jello_medium_1_like', 'Jello_medium_1_want', 'Jello_medium_1_familiar', 'Jello_medium_1_creamy', 'Jello_medium_1_fatty', 'Jello_low_2_intense', 'Jello_low_2_sweet', 'Jello_low_2_like', 'Jello_low_2_want', 'Jello_low_2_familiar', 'Jello_low_2_creamy', 'Jello_low_2_fatty', 'Jello_medium_2_intense', 'Jello_medium_2_sweet', 'Jello_medium_2_like', 'Jello_medium_2_want', 'Jello_medium_2_familiar', 'Jello_medium_2_creamy', 'Jello_medium_2_fatty', 'Jello_medium_3_intense', 'Jello_medium_3_sweet', 'Jello_medium_3_like', 'Jello_medium_3_want', 'Jello_medium_3_familiar', 'Jello_medium_3_creamy', 'Jello_medium_3_fatty', 'Jello_low_3_intense', 'Jello_low_3_sweet', 'Jello_low_3_like', 'Jello_low_3_want', 'Jello_low_3_familiar', 'Jello_low_3_creamy', 'Jello_low_3_fatty', 'Jello_high_2_intense', 'Jello_high_2_sweet', 'Jello_high_2_like', 'Jello_high_2_want', 'Jello_high_2_familiar', 'Jello_high_2_creamy', 'Jello_high_2_fatty', 'Jello_high_3_intense', 'Jello_high_3_sweet', 'Jello_high_3_like', 'Jello_high_3_want', 'Jello_high_3_familiar', 'Jello_high_3_creamy', 'Jello_high_3_fatty', 'Jello_0_3_intense', 'Jello_0_3_sweet', 'Jello_0_3_like', 'Jello_0_3_want', 'Jello_0_3_familiar', 'Jello_0_3_creamy', 'Jello_0_3_fatty', 'Pudding_high_1_intense', 'Pudding_high_1_sweet', 'Pudding_high_1_like', 'Pudding_high_1_want', 'Pudding_high_1_familiar', 'Pudding_high_1_creamy', 'Pudding_high_1_fatty', 'Pudding_0_1_intense', 'Pudding_0_1_sweet', 'Pudding_0_1_like', 'Pudding_0_1_want', 'Pudding_0_1_familiar', 'Pudding_0_1_creamy', 'Pudding_0_1_fatty', 'Pudding_low_1_intense', 'Pudding_low_1_sweet', 'Pudding_low_1_like', 'Pudding_low_1_want', 'Pudding_low_1_familiar', 'Pudding_low_1_creamy', 'Pudding_low_1_fatty', 'Pudding_high_2_intense', 'Pudding_high_2_sweet', 'Pudding_high_2_like', 'Pudding_high_2_want', 'Pudding_high_2_familiar', 'Pudding_high_2_creamy', 'Pudding_high_2_fatty', 'Pudding_0_2_intense', 'Pudding_0_2_sweet', 'Pudding_0_2_like', 'Pudding_0_2_want', 'Pudding_0_2_familiar', 'Pudding_0_2_creamy', 'Pudding_0_2_fatty', 'Pudding_low_2_intense', 'Pudding_low_2_sweet', 'Pudding_low_2_like', 'Pudding_low_2_want', 'Pudding_low_2_familiar', 'Pudding_low_2_creamy', 'Pudding_low_2_fatty', 'Pudding_medium_1_intense', 'Pudding_medium_1_sweet', 'Pudding_medium_1_like', 'Pudding_medium_1_want', 'Pudding_medium_1_familiar', 'Pudding_medium_1_creamy', 'Pudding_medium_1_fatty', 'Pudding_0_3_intense', 'Pudding_0_3_sweet', 'Pudding_0_3_like', 'Pudding_0_3_want', 'Pudding_0_3_familiar', 'Pudding_0_3_creamy', 'Pudding_0_3_fatty', 'Pudding_low_3_intense', 'Pudding_low_3_sweet', 'Pudding_low_3_like', 'Pudding_low_3_want', 'Pudding_low_3_familiar', 'Pudding_low_3_creamy', 'Pudding_low_3_fatty', 'Pudding_high_3_intense', 'Pudding_high_3_sweet', 'Pudding_high_3_like', 'Pudding_high_3_want', 'Pudding_high_3_familiar', 'Pudding_high_3_creamy', 'Pudding_high_3_fatty', 'Pudding_medium_2_intense', 'Pudding_medium_2_sweet', 'Pudding_medium_2_like', 'Pudding_medium_2_want', 'Pudding_medium_2_familiar', 'Pudding_medium_2_creamy', 'Pudding_medium_2_fatty', 'Pudding_medium_3_intense', 'Pudding_medium_3_sweet', 'Pudding_medium_3_like', 'Pudding_medium_3_want', 'Pudding_medium_3_familiar', 'Pudding_medium_3_creamy', 'Pudding_medium_3_fatty', 'post_hungry', 'post_full', 'post_thirsty', 'post_anxious', 'post_pee']
		writer = csv.DictWriter(f, fieldnames)
		writer.writeheader()
		for root, dirs, files in os.walk("./data"):
			for file in files:
				subj_id = file[0:4]
				rf_name = subj_id + "_preference_randomization.xlsx"
				if rf_name not in rands:
					subjects_without_randomization_file.add(subj_id)
				else:
					pref = "./data/" + file
					rand = "./" + RANDS + rf_name
					results = fat_sugar_score(pref, rand, subj_id)
					writer.writerow(results)

	print(subjects_without_randomization_file)

	# loop through files for which we have both preference ratings and randomization, adding results to out_all
	# write results of out_all to a csv
	# pref = "test.csv"
	# rand = "rand.xlsx"
	# results = fat_sugar_score(pref, rand)

