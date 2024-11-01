# Name: Main_parallelized
#
# Version: 4.0
#
# Author: Anish Vasan
#
# Organization: Chen/Eyckmans Lab, Boston University
#
# Date: 20241030

# IMPORTS #


from wc_functions import *
from GUI_functions import *


# DEFINITIONS #
# These require user input/changes based on experiments - now entered through GUI #
if __name__ == "__main__":

    image_type, is_pillars, cpu_threshold, ms_choice, section2, section3, section4 = input_gui()
    is_fl = False  # Options: True, False

    # RUN CODE #


    # **Section 1: Navigate to data folder containing .nd file or experiment files** #

    print("Current config:")
    print(cpu_threshold)
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
        print('.nd file found:', is_nd)

        # Sort images in input folder into Sorted/basename/ folders
        print("Sorting images into corresponding basename folders...")
        sort_basename_folders(basename_list, path_input, path_output, ms_choice)
        print("Completed!")

        # Extract stage position information from .nd file or from data in folder
        stage_pos_nd, stage_pos_maps, timepoints_list = extract_nd_info(basename_list, path_output, is_nd, ms_choice)
        print("Extracted stage position information")
        print(stage_pos_maps)
        #  Sort images in each basename folder into their corresponding stage position folders
        print("Sorting images in each basename folder into their corresponding stage position folders...")
        sort_stage_pos_folders(basename_list, path_output, stage_pos_maps, image_type, ms_choice, is_nd)

        print("Completed")

    else:
        basename_list = os.listdir(path_input)
        basename_list = [name for name in basename_list if os.path.isdir(os.path.join(path_input, name))]

    # **Section 3: Execute woundcomputes in parallel** #
    if section3:

        print("Starting wound compute for each experiment folder...")
        print("Start time:", time.ctime())

        for index, basename in enumerate(basename_list):
            print("Processing folder:", basename)
            cpu_threshold = 80
            print("CPU Threshold:", cpu_threshold)
            process_folder(os.path.join(path_output, basename), cpu_threshold)


        print("Completed! Hurray!")
        print("End time:", time.ctime())
        print("Total time taken:", format_timespan(time.time() - time_start))

    # **Section 4: Extract data from folders and create database and Excel output** #
    if section4:
        # Call the WellPlate Interface and get condition assignments from user
        #GUI_root = tk.Tk()
        #app = WellPlateInterface(master_in=GUI_root,
        #                         stage_pos_map_in=stage_pos_maps,
        #                         basename_in=basename)
        #GUI_root.mainloop()

        # Access the dataframe after closing the interface
        #assigned_df = app.get_assigned_dataframe()
        #print(assigned_df)



        print(basename_list)
        for index, basename in enumerate(basename_list):
            extract_data(path_output, basename, image_type)
            print("Data extracted to excel file in ", basename)





