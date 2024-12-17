# Name: Main_parallelized
#
# Version: 4.3
#
# Author: Anish Vasan
#
# Organization: Chen/Eyckmans Lab, Boston University
#
# Date: 20241104
# IMPORTS #
import os
import tkinter as tk
from wc_functions import *
from wc_GUI_functions import *
from wc_data_functions import *


# DEFINITIONS #
# These require user input/changes based on experiments - now entered through GUI #
if __name__ == "__main__":

    image_type, is_pillars, cpu_threshold, ms_choice, imaging_interval, section2, section3, section4, section5 = input_gui()

    # RUN CODE #


    # **Section 1: Navigate to data folder containing .nd file or experiment files** #

    print("Current config:")
    print("CPU Utilization Threshold:", cpu_threshold, "%")
    print("Image Type:", image_type)
    print("Track Pillars:", is_pillars)
    print("Data Type:", ms_choice)
    path_input, path_output = io_function(section2)

    # **Section 2: Execute functions to prepare folder structure for WoundCompute** #
    if section2:
        # Create yaml file for image type
        create_wc_yaml(path_output, image_type, is_pillars)
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
        stage_pos_maps = extract_nd_info(basename_list, path_output, is_nd, ms_choice)
        print("Extracted stage position information")
        print(stage_pos_maps)
        #  Sort images in each basename folder into their corresponding stage position folders
        print("Sorting images in each basename folder into their corresponding stage position folders...")
        efficient_sort_stage_pos(basename_list, path_output, stage_pos_maps, image_type, ms_choice, is_nd)

        print("Completed")

    else:
        # If section2 is False, then the user has already prepared the folder structure
        # and the program will directly go to section 3
        # Open and read the YAML file
        file_list = os.listdir(path_output)
        if 'basename_list.yaml' in file_list:
            print("Found basename_list.yaml file in the input folder")
            with open(os.path.join(path_output, 'basename_list.yaml'), 'r') as file:
                # Load the YAML content
                basename_list = yaml.safe_load(file)

        else:
            # If basename.yaml file is not found, then get the list of folders in the input folder
            # and set it as the basename list
            basename_list = os.listdir(path_output)
            basename_list = [name for name in basename_list if os.path.isdir(os.path.join(path_output, name))]

        if 'stage_positions.yaml' in file_list:
            print("Found stage_positions.yaml file in the input folder")
            with open(os.path.join(path_input, 'stage_positions.yaml'), 'r') as file:
                # Load the YAML content
                data = yaml.safe_load(file)

            stage_pos_maps = {}
            for index, basename in enumerate(basename_list):
                stage_pos_maps[basename] = data[basename]

        else:
            # If stage_positions.yaml file is not found, then get the list of folders in the basename folder
            # and set it as the stage_pos_maps
            stage_pos_maps = {}
            for index, basename in enumerate(basename_list):
                path_temp = os.path.join(path_output, Path(basename))
                positions = os.listdir(path_temp)
                positions.sort()
                positions = [n1 for n1 in positions if not n1.endswith('.nd')]
                stage_pos_maps[basename] = {N: position for N, position in zip(range(1, len(positions) + 1), positions)}

    # **Section 3: Execute WoundCompute instances in parallel** #
    if section3:
        time_start = time.time()
        print("Starting wound compute for each experiment folder...")
        print("Start time:", time.ctime())

        for index, basename in enumerate(basename_list):
            print("Processing folder:", basename)
            wc_process_folder(os.path.join(path_output, basename), cpu_threshold)


        print("Completed! Hurray!")
        print("End time:", time.ctime())
        print("Total time taken:", format_timespan(time.time() - time_start))

    # **Section 4: Extract data from folders and create database and Excel output** #
    if section4:
        for index, basename in enumerate(basename_list):

            if os.path.join(path_output, 'code_output_' + basename + '.xlsx'):
                print("Found existing condition map file.")
                try:
                    df_assignments = pd.read_excel(os.path.join(path_output, 'code_output_' + basename + '.xlsx'),
                                        sheet_name='condition_map')
                except Exception as e:
                    print("Error reading condition map file:", e)
                    df_assignments = None
            else:
                df_assignments = None

            if df_assignments is None:
                #Call the WellPlate Interface and get condition assignments from user
                GUI_root = tk.Tk()
                print(stage_pos_maps[basename])
                app = WellPlateInterface(master_in=GUI_root, path_input_in=path_output,
                                         stage_pos_map_in=stage_pos_maps[basename],
                                         basename_in=basename_list[index])
                GUI_root.mainloop()

                # Access the dataframe after closing the interface
                df_assignments = app.get_assigned_dataframe()
                append_to_excel(os.path.join(path_output, 'code_output_' + basename + '.xlsx'), df_assignments,
                                'condition_map')
                GUI_root.destroy()
                print("Condition map saved to excel file")

            # Extract data from the folders and create an Excel file
            all_data, metrics, positions = extract_data(path_output, basename, image_type, imaging_interval,df_assignments)
            print("Data extracted to excel file in ", basename + ".xlsx")

            #Group data by conditions
            df_grouped = group_data(all_data, metrics, positions, df_assignments)

            # **Section 5: Visualize data** #
            if section5:
                visualize_data(path_output, basename, all_data, metrics, positions, df_assignments)

            messy_requests(path_output_in=path_output, basename_in=basename, df_grouped_in=df_grouped, all_data_in=all_data)








