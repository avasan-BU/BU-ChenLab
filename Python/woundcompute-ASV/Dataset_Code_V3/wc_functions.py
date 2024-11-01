# Name: wc_functions
#
# Version: 2.8
#
# Author: Anish Vasan
#
# Organization: Chen/Eyckmans Lab, Boston University
#
# Date: 20240821


import fnmatch
import os
import shutil
import tkinter
import yaml
import subprocess
import tkinter as tk
from tkinter.filedialog import askdirectory
from tkinter import simpledialog
import time
from humanfriendly import format_timespan
from woundcompute import image_analysis as ia
from pathlib import Path
import sys
import pandas as pd
import openpyxl
import re
import psutil
import time
from concurrent.futures import ProcessPoolExecutor, as_completed, wait, FIRST_COMPLETED

#  Information Extraction Functions
def create_yaml(path: str, image_type_in: str, is_fl_in: bool, is_pillars_in: bool):
    """Given the output path as string. Will create a yaml file in the main output folder. This yaml file will be
    copied into each subfolder during the sorting function"""

    # Default keys and values stored in yaml file
    yaml_input_file = {
        'version': 1.0,
        'segment_brightfield': False,
        'seg_bf_version': 1,
        'seg_bf_visualize': False,
        'segment_fluorescent': False,
        'seg_fl_version': 1,
        'seg_fl_visualize': False,
        'segment_ph1': True,  # True,
        'seg_ph1_version': 2,
        'seg_ph1_visualize': True,
        'track_brightfield': False,
        'track_bf_version': 1,
        'track_bf_visualize': False,
        'track_ph1': False,
        'track_ph1_version': 1,
        'track_ph1_visualize': False,
        'bf_seg_with_fl_seg_visualize': False,
        'bf_track_with_fl_seg_visualize': False,
        'ph1_seg_with_fl_seg_visualize': False,
        'ph1_track_with_fl_seg_visualize': False,
        'zoom_type': 2,
        'track_pillars_ph1': False
    }

    # Conditionally modify yaml file based on image_type input

    for key, value in yaml_input_file.items():
        if image_type_in in key and not "version" in key and not "fl" in key and not "track" in key:
            yaml_input_file[key] = True

            if is_fl_in:
                if "fl" in key and not "version" in key:
                    yaml_input_file[key] = True

            if is_pillars_in:
                if "pillars" in key and not "version" in key:
                    yaml_input_file[key] = True

    # Write yaml output to path_output
    with open(os.path.join(path, 'wc_dataset_' + image_type_in + '.yaml'), 'w') as file:
        yaml.safe_dump(yaml_input_file, file, sort_keys=False)


def define_basename_list(path_input_fn: str, path_output_fn: str, ms_choice: str) -> (list, bool):
    """Given an input path as a string. Will return a list of experiment names in the input folder"""

    is_nd_out = False
    basename_list_fn = []

    if ms_choice == "Cytation":
        basename_list_fn = [name for name in os.listdir(path_input_fn) if
                            os.path.isdir(os.path.join(path_input_fn, name))]
        basename_list_fn = [name for name in basename_list_fn if
                            not os.path.join(path_input_fn, name) == path_output_fn]
        basename_list_fn = [name for name in basename_list_fn if not os.path.join(path_input_fn, name) == os.path.join(path_input_fn, 'Sorted')]

    else:
        for file in os.listdir(path_input_fn):
            if file.endswith('.nd'):
                name, ext = os.path.splitext(file)
                basename_list_fn.append(name)
                is_nd_out = True

        if not is_nd_out:
            file_list = os.listdir(path_input_fn)
            basename = [file.split('_') for file in file_list if file.endswith('.tif') or file.endswith('.TIF')]
            basename = list(dict.fromkeys(["_".join([str(item1) for item1 in item[0:-2]]) for item in basename]))
            basename_list_fn = [b for b in basename if 'thumb' not in b]

    return basename_list_fn, is_nd_out


def extract_nd_info(basename_list_fn: list, path_output_fn: str, is_nd: bool, ms_choice: str) -> (list, dict):
    """Given a basename list and an output path. Will extract number of stage positions for each list and create
    position map lists for each basename"""

    stage_positions = []
    timepoints_list = []
    stage_pos_maps = {}
    stage_pos_submap = {}
    if is_nd:
        for index_fn, basename_fn in enumerate(basename_list_fn):
            with open(os.path.join(path_output_fn, basename_fn, basename_fn + '.nd'), 'r') as nd_file:
                print("Opened .nd")
                for l_no, line in enumerate(nd_file):
                    if '"NStagePositions"' in line:
                        spos_int = [int(s) for s in line.split() if s.isdigit()][-1]
                        stage_positions.append(spos_int)
                        stage_pos_submap = {}
                        for l_no1, line1 in enumerate(nd_file):
                            for N in range(1, spos_int+1):
                                if '"Stage' + str(N) + '"' in line1:
                                    sp_well = line1.split('"')[-2]
                                    stage_pos_submap[N] = sp_well
                        break
            stage_pos_maps[basename_fn] = stage_pos_submap
            print("Extracted information from .nd file")
    else:
        for index_fn, basename_fn in enumerate(basename_list_fn):
            file_list = os.listdir(os.path.join(path_output_fn, basename_fn))

            timepoints = [file.split('_')[-1].split('.')[0] for file in file_list if
                          file.endswith('.tif') or file.endswith('.TIF')]
            timepoints = list(dict.fromkeys(timepoints))
            timepoints_list.append(len(timepoints))

            if ms_choice == "Cytation":
                positions = [file.split('_')[0] for file in file_list if
                             file.endswith('.tif') or file.endswith('.TIF')]
            else:
                positions = [file.split('_')[-2] for file in file_list if
                             file.endswith('.tif') or file.endswith('.TIF')]
            positions = list(dict.fromkeys(positions))
            stage_positions.append(len(positions))

            positions = [pos[:1] + pos[1:].zfill(2) for pos in positions]
            positions.sort()
            stage_pos_submaps = {N: position for N, position in zip(range(1, len(positions) + 1), positions)}
            stage_pos_maps[basename_fn] = stage_pos_submaps
            print("Extracted information from files in folder")

    return stage_positions, stage_pos_maps, timepoints_list


# Folder Organization Functions
def sort_basename_folders(basename_list_fn: list, path_input_fn: str, path_output_fn: str, ms_choice: str):
    """Given a list of experiments obtained from the .nd files in the input folder. Given input and out paths as str.
 Creates an output folder at path_output. Copies and sorts TIFF files in path_input according to basenames in output
 folder"""

    for basename_fn in basename_list_fn:

        # create folders for each expt
        try:
            os.makedirs(os.path.join(path_output_fn, basename_fn))
        except OSError as e:
            # If it fails, inform the user.
            print('Error: %s - %s.' % (e.filename, e.strerror))

        if ms_choice == "Cytation":
            path_temp = os.path.join(path_input_fn, basename_fn)

            for file in os.listdir(path_temp):
                if file.endswith('.tif' or '.TIF'):
                    try:
                        shutil.copy(os.path.join(path_temp, file), os.path.join(path_output_fn, basename_fn, file))
                    except OSError as e:
                        # If it fails, inform the user.
                        print('Error: %s - %s.' % (e.filename, e.strerror))
        else:
            # copy .nd file into respective basename folder
            if os.path.isfile(os.path.join(path_input_fn, basename_fn + '.nd')):
                try:
                    shutil.copy(os.path.join(path_input_fn, basename_fn + '.nd'),
                                os.path.join(path_output_fn, basename_fn, basename_fn + '.nd'))
                except OSError as e:
                    # If it fails, inform the user.
                    print('Error: %s - %s.' % (e.filename, e.strerror))

            # copy TIF files to respective basename folders, excludes thumbnail files
            for file in os.listdir(path_input_fn):
                if file.startswith(basename_fn + '_') and not fnmatch.fnmatch(file, '*thumb*'):
                    try:
                        shutil.copy(os.path.join(path_input_fn, file), os.path.join(path_output_fn, basename_fn, file))
                    except OSError as e:
                        # If it fails, inform the user.
                        print('Error: %s - %s.' % (e.filename, e.strerror))


def sort_stage_pos_folders(basename_list_fn: list, parent_output_fn: str,
                           stage_pos_maps_fn: dict, image_type_fn: str, ms_choice: str, is_nd: bool):
    """Given basename list, parent output folder and number of stage positions list extracted from nd files. Sorts
    files into stage position folders"""
    # sort images into stage position folders
    verbose = False
    for index_fn, basename_fn in enumerate(basename_list_fn):
        filelist = os.listdir(os.path.join(parent_output_fn, basename_fn))
        filelist.sort()
        for file in filelist:
            if verbose:
                print(file)
            if file.casefold().endswith('.tif'):
                if verbose:
                    print('found tif')

                #Define pattern to recognize timepoint and stage position
                timepoint_pattern = r't(\d+)'
                stage_pattern_s = r's(\d+)'
                stage_pattern_letter = r'([A-H])(\d+)'
                new_filename = file
                # Find timepoint and stage position
                timepoint_match = re.search(timepoint_pattern, file)
                stage_wellpos_match = re.search(stage_pattern_letter, file)
                stage_match_s = re.search(stage_pattern_s, file)

                # Rename timepoint and stage position to have 3 digits
                if timepoint_match:
                    old_timepoint = timepoint_match.group(0)
                    timepoint_num = int(timepoint_match.group(1))
                    new_timepoint = f't{timepoint_num:03d}'
                    new_filename = new_filename.replace(old_timepoint, new_timepoint)

                # Identify the stage position
                if stage_wellpos_match:
                    spos = stage_wellpos_match.group(0)
                # If the stage position is formatted as 'sX or sXX' where X is a digit then rename to 'sXXX'
                elif stage_match_s:
                    old_stage = stage_match_s.group(0)
                    stage_num = int(stage_match_s.group(1))
                    spos = f's{stage_num:03d}'
                    if is_nd:
                        spos = spos + '_' + stage_pos_maps_fn[basename_fn][int(spos.split('s')[-1])]
                    new_filename = new_filename.replace(old_stage, spos)




                path_input_fn = os.path.join(parent_output_fn, basename_fn)
                path_pos_output_fn = os.path.join(parent_output_fn, basename_fn, spos)

                # check if stage position directory already exists and move file into this folder if it does
                if os.path.exists(os.path.join(path_pos_output_fn, image_type_fn + '_images')):
                    try:
                        shutil.move(os.path.join(path_input_fn, file),
                                    os.path.join(path_pos_output_fn, image_type_fn + '_images', new_filename))
                    except OSError as e:
                        # If it fails, inform the user.
                        print('Error: %s - %s.' % (e.filename, e.strerror))

                # otherwise, create folder and move file into this folder. Also copy parent yaml file into this
                # folder.
                else:
                    try:
                        os.makedirs(os.path.join(path_pos_output_fn, image_type_fn + '_images'))
                        shutil.copy(os.path.join(parent_output_fn, 'wc_dataset_' + image_type_fn + '.yaml'),
                                    os.path.join(path_pos_output_fn, 'wc_dataset_' + image_type_fn + '.yaml'))
                        if verbose:
                            print("copying yaml")
                        shutil.move(os.path.join(path_input_fn, file),
                                    os.path.join(path_pos_output_fn, image_type_fn + '_images', new_filename))
                        if verbose:
                            print("moving file:", file)


                    except OSError as e:
                        # If it fails, inform the user.
                        print('Error: %s - %s.' % (e.filename, e.strerror))


# WoundCompute Functions


def woundcompute_run(input_path_fn: str):
    # ** Section 3: Execute woundcompute for all basename folders in the Sorted folder ** #
    time_all = []
    current = time.time()
    try:
        time_all, action_all = ia.run_all(Path(input_path_fn))
        secondsPassed = time.time() - current
        print("Processing: ", input_path_fn, "  Tissue: ", os.path.basename(os.path.normpath(input_path_fn)), "     time: ",
                format_timespan(secondsPassed))
    except Exception as ex:
        time_all.append(time.time())
        print("Path: ", input_path_fn, "    Tissue: ", os.path.basename(os.path.normpath(input_path_fn)), "     time: ",
                  time.ctime())
        print("---------ERROR OF SOME DESCRIPTION HAS HAPPENED-------")
        print(ex)
        print("------------------------------------------------------")


def sort_back_to_main(parent_input_fn: str, subfolder_input_fn: str):
    filelist = os.listdir(subfolder_input_fn)
    filelist.sort()
    for file in filelist:
        try:
            shutil.move(os.path.join(subfolder_input_fn, file), os.path.join(parent_input_fn, file))
        except OSError as e:
            # If it fails, inform the user.
            print('Error: %s - %s.' % (e.filename, e.strerror))

    if not os.listdir(subfolder_input_fn):
        try:
            os.rmdir(subfolder_input_fn)
        except OSError as e:
            # If it fails, inform the user.
            print('Error: %s - %s.' % (e.filename, e.strerror))


def extract_data(path_output_fn: str, basename_fn: str, image_type: str):
    input_path_fn = os.path.join(path_output_fn, basename_fn)
    folder_list = os.listdir(input_path_fn)
    folder_list.sort()
    folder_list = [n1 for n1 in folder_list if not n1.endswith('.nd')]

    frames = len(os.listdir(os.path.join(input_path_fn, folder_list[0], image_type + "_images")))
    tlist = [T * 0.5 for T in range(0, frames)]
    df_woundarea = pd.DataFrame({'Frame': range(1, frames + 1), 'Time': tlist})
    df_isclosed = pd.DataFrame({'Frame': range(1, frames + 1), 'Time': tlist})
    df_isbroken = pd.DataFrame({'Frame': range(1, frames + 1), 'Time': tlist})

    for file in folder_list:
        if os.path.isfile(os.path.join(input_path_fn, file, 'segment_' + image_type, 'wound_area_vs_frame.txt')):
            df_woundarea[file] = pd.read_table(os.path.join(input_path_fn, file, 'segment_' + image_type, 'wound_area_vs_frame.txt'), header=None)
            df_isclosed[file] = pd.read_table(os.path.join(input_path_fn, file, 'segment_' + image_type, 'is_closed_vs_frame.txt'), header=None)
            df_isbroken[file] = pd.read_table(os.path.join(input_path_fn, file, 'segment_' + image_type, 'is_broken_vs_frame.txt'), header=None)

        else:
            df_woundarea[file] = [0]*frames
            df_isclosed[file] = [0]*frames
            df_isbroken[file] = [0]*frames

    workbook = openpyxl.Workbook()
    workbook.save(os.path.join(path_output_fn, 'code_output_' + basename_fn + '.xlsx'))

    append_to_excel(os.path.join(path_output_fn, 'code_output_' + basename_fn + '.xlsx'), df_woundarea, "wound_area")
    append_to_excel(os.path.join(path_output_fn, 'code_output_' + basename_fn + '.xlsx'), df_isclosed, "is_closed")
    append_to_excel(os.path.join(path_output_fn, 'code_output_' + basename_fn + '.xlsx'), df_isbroken, "is_broken")


def append_to_excel(fpath, df, sheet_name):
    with pd.ExcelWriter(fpath, mode="a", if_sheet_exists='replace') as f:
        df.to_excel(f, sheet_name=sheet_name)


# Parallel Processing handlers

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def process_folder(main_folder, cpu_threshold):
    # Get all subfolders in the main folder
    subfolders = [f.path for f in os.scandir(main_folder) if f.is_dir()]

    with ProcessPoolExecutor() as executor:
        futures = []
        for subfolder in subfolders:
            while True:
                cpu_usage = get_cpu_usage()
                if cpu_usage < cpu_threshold:
                    future = executor.submit(woundcompute_run, subfolder)
                    futures.append(future)
                    break
                else:
                    # Wait for a future to complete before adding more
                    if futures:
                        done, _ = executor.wait(futures, return_when='FIRST_COMPLETED')
                        for completed_future in done:
                            futures.remove(completed_future)
                    else:
                        time.sleep(0.1)  # Short sleep to prevent busy waiting

        # Wait for all remaining futures to complete
        for future in as_completed(futures):
            pass


