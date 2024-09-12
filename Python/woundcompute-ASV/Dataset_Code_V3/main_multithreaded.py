# Name: Main_multithreader
#
# Version: 1.8
#
# Author: Anish Vasan
#
# Organization: Chen/Eyckmans Lab, Boston University
#
# Date: 20240815

# IMPORTS #

import threading
from wc_functions import *
import sys

# DEFINITIONS #
# These require user input/changes based on experiments - now entered through GUI #

image_type, is_pillars, parallels, ms_choice, section2, section3, section4 = input_gui()
is_fl = False  # Options: True, False

# RUN CODE #


# **Section 1: Navigate to data folder containing .nd file or experiment files** #

print("Current config:")
print("Image Type:", image_type)
print("Fluorescent Images:", is_fl)
print("Track Pillars:", is_pillars)
print(ms_choice)
path_input, path_output = io_function(section2)

# **Section 2: Execute functions to prepare folder structure for woundcompute** #
if section2:
    # Create yaml file for image type
    create_yaml(path_output, image_type, is_fl, is_pillars)
    print("Created .yaml file")

    # Create list of .nd files/experiments in the input folder
    basename_list, is_nd = define_basename_list(path_input, path_output, ms_choice)
    print("Created basename list:", basename_list)
    print(is_nd)

    # Sort images in input folder into Sorted/basename/ folders
    print("Sorting images into corresponding basename folders...")
    sort_basename_folders(basename_list, path_input, path_output, ms_choice)
    print("Completed!")

    # Extract stage position information from .nd file or from data in folder
    stage_pos_nd, stage_pos_maps, timepoints_list = extract_nd_info(basename_list, path_output, is_nd, ms_choice)
    print("Extracted stage position information")
    print(stage_pos_nd)
    print(stage_pos_maps)
    print(timepoints_list)
    #  Sort images in each basename folder into their corresponding stage position folders
    print("Sorting images in each basename folder into their corresponding stage position folders...")
    sort_stage_pos_folders(basename_list, path_output, stage_pos_maps, image_type, ms_choice, is_nd)

    # Divide tissue folders into processing groups to maximize processing power
    print("Dividing tissue folders into processing subfolders to maximize multicore performance...")
    sort_parallel_processes(basename_list, path_output, parallels, is_nd)

    print("Completed")

else:
    basename_list = os.listdir(path_input)
    basename_list = [name for name in basename_list if os.path.isdir(os.path.join(path_input, name))]

# **Section 3: Execute woundcomputes in parallel** #
if section3:
    for index, basename in enumerate(basename_list):
        processes = []
        start = time.time()

        print("Starting wound compute for each stage position...")
        print("Start time:", time.ctime())
        for thread_count in range(1, parallels + 1):
            input_location = os.path.join(path_output, basename, 'p' + f"{thread_count:02}")
            if __name__ == "__main__":
                thread_handle = threading.Thread(target=run_threads, args=(
                    os.path.join(sys.path[0], 'multithread_processes', 'thread' + str(f"{thread_count:02}") + '.py'), input_location,))
                thread_handle.start()
                processes.append(thread_handle)
        for thread_handle_j in processes:
            thread_handle_j.join()

        for thread_count in range(1, parallels + 1):
            input_location = os.path.join(path_output, basename, 'p' + f"{thread_count:02}")
            sort_back_to_main(os.path.join(path_output, basename), input_location)

        print("Files moved back to basename folder")
        print("All ", parallels, " threads have finished running for " + basename)
        print("Completed! Hurray!")
        print("End time:", time.ctime())
        print("Total time taken:", format_timespan(time.time() - start))
        print("Please run extract_dataset to consolidate outputs into an excel file!")


# **Section 4: Extract data from folders and create database and Excel output** #
if section4:

    print(basename_list)
    for index, basename in enumerate(basename_list):
        extract_data(path_output, basename, image_type)
        print("Data extracted to excel file in ", basename)





