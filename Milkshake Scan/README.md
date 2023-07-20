# Milkshake Scan scoring
This script takes a folder with raw PsychoPy output, as outlined in Peirce et al. 2019, containing all subjects you wish to score. It outputs a 'scored/' folder containing corresponding MATLAB vector files for each subject.

# Tweaking the script for your own task
This script is specific to the usage of the Modern Diet and Physiology Research Center in several ways. First of all, subject data files follow the naming scheme, "XXXX_filename," where XXXX is the 4-digit identification number assigned to our subjects. To accomodate other ID or file naming schemes, the "main" function should be revised.

The script was used to score scans at the baseline appointment. Its output vectors follow the naming scheme, "baseline_milkshake_XXXX.m." This can also be changed to a more appropriate name. 
