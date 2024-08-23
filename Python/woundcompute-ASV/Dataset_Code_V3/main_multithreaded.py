# Name: Main_multithreader
#
# Version: 1.4
#
# Author: Anish Vasan
#
# Organization: Chen/Eyckmans Lab, Boston University
#
# Date: 20240815

# IMPORTS #

import threading
from wc_functions_2_2 import *
import sys

# DEFINITIONS #
# These require user input/changes based on experiments #

image_type, is_pillars, parallels, ms_choice, section2, section3 = input_gui()
is_pillars = bool(is_pillars)
is_fl = False  # Options: True, False

# RUN CODE #


# **Section 1: Navigate to data folder containing .nd file** #

print("Current config:")
print("Image Type:", image_type)
print("Fluorescent Images:", is_fl)
print("Track Pillars:", is_pillars)

path_input, path_output = io_function()

# **Section 2: Execute functions to prepare folder structure for woundcompute** #


# Create yaml file for image type
create_yaml(path_output, image_type, is_fl, is_pillars)
print("Created .yaml file")

# Create list of .nd files/experiments in the input folder
basename_list = define_basename_list(path_input)
print("Created basename list:", basename_list)

# Sort images in input folder into Sorted/basename folder
print("Sorting images into corresponding basename folders...")
sort_basename_folders(basename_list, path_input, path_output)
print("Completed!")

# Extract stage position information from .nd file
stage_pos_nd = extract_nd_info(basename_list, path_output)
print("Extracted stage position information from .nd files")

#  Sort images in each basename folder into their corresponding stage position folders
print("Sorting images in each basename folder into their corresponding stage position folders...")
sort_stage_pos_folders(basename_list, path_output, stage_pos_nd, image_type)

# Divide tissue folders into processing groups to maximize processing power
print("Dividing tissue folders into processing subfolders to maximize multicore performance...")
sort_parallel_processes(basename_list, path_output, stage_pos_nd, image_type, parallels)

print("Completed")

# **Section 3: Execute woundcomputes in parallel** #


for index, basename in enumerate(basename_list):
    processes = []
    start = time.time()

    print("Starting wound compute for each stage position...")
    print("Start time:", time.ctime())
    for thread_count in range(1, parallels + 1):
        input_location = Path(path_output + '/' + basename + '/' + 'p' + f"{thread_count:02}")
        if __name__ == "__main__":
            thread_handle = threading.Thread(target=run_threads, args=(sys.path[0] + '/multithread_processes/thread' + str(f"{thread_count:02}") + '.py', input_location,))
            thread_handle.start()
            processes.append(thread_handle)
    for thread_handle_j in processes:
        thread_handle_j.join()

    print("All ", parallels, " threads have finished running for " + basename)
    print("Completed! Hurray!")
    print("End time:", time.ctime())
    print("Total time taken:", format_timespan(time.time() - start))
    print("Please run extract_dataset to consolidate outputs into an excel file!")
