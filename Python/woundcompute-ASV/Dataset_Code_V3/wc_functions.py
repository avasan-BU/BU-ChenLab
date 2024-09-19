# Name: wc_functions
#
# Version: 2.6
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
from tkinter.filedialog import askdirectory
from tkinter import simpledialog
import time
from humanfriendly import format_timespan
from woundcompute import image_analysis as ia
from pathlib import Path
import sys
import pandas as pd
import openpyxl


# GUI Functions
def io_function(section2: bool) -> (str, str):
    """Prompt user for input folder that contains a .nd file"""
    # prompt user for the file directory. Will open as a popup window named "tk"
    tk_root = tkinter.Tk()
    print("Please open the directory that contains your .nd file")
    path_input = askdirectory(title='Select Input Folder with .nd file')  # shows dialog box and return the path
    if path_input == "":
        print("No folder selected. Program exiting.")
        quit()
    else:
        print("Inputed path:", path_input)

    if section2:
        path_output = os.path.join(path_input, 'Sorted')

        if os.path.exists(path_output):
            path_out_new = simpledialog.askstring('Output folder', 'Enter new output folder name')
            # path_out_new = input('Enter new output folder name')
            if path_out_new == "":
                print("No folder selected. Program exiting.")
                quit()
            path_output = os.path.join(path_input, path_out_new)

        # create a new  output directory

        os.makedirs(path_output)
    else:
        path_output = path_input
    tk_root.destroy()
    return path_input, path_output


def input_gui() -> (str, bool, int, str, bool, bool, bool):
    # Create object
    window = tkinter.Tk()

    # Adjust size
    # window.geometry("400x400")

    # Close window after storing variables
    def accept():
        window.destroy()

    def killmenow():
        sys.exit()

    # Menu for Microscope Type

    # Dropdown menu options

    options_microscope_type = [
        "Eclipse Ti",
        "Eclipse Ti 2 - Spectra",
        "Cytation"
    ]

    # datatype of menu text
    microscope_type_clicked = tkinter.StringVar()

    # Create Label
    label_microscope_type = tkinter.Label(window, text="Source Microscope:")
    label_microscope_type.pack()

    # initial menu text
    microscope_type_clicked.set("Eclipse Ti")

    # Create Dropdown menu
    drop1 = tkinter.OptionMenu(window, microscope_type_clicked, *options_microscope_type)
    drop1.pack()

    # Menu for Image Type

    # Dropdown menu options
    options_image_type = [
        "ph1",
        "BF",
    ]

    # datatype of menu text
    image_type_clicked = tkinter.StringVar()

    # Create Label
    label_image_type = tkinter.Label(window, text="Image Type:")
    label_image_type.pack()

    # initial menu text
    image_type_clicked.set("ph1")

    # Create Dropdown menu
    drop1 = tkinter.OptionMenu(window, image_type_clicked, *options_image_type)
    drop1.pack()

    # Menu for number of Parallel Processes

    # datatype of menu text

    parallel_processes_clicked = tkinter.IntVar(value=8)

    # Create Label
    label_parallel_processes = tkinter.Label(window, text="Number of Parallel Processes:")
    label_parallel_processes.pack()

    # Create Dropdown menu
    scale = tkinter.Scale(window, from_=1, to=12, orient="horizontal", variable=parallel_processes_clicked)
    scale.pack(side="top", fill="x")

    # Menu for Pillar Tracking
    # Create checkbox
    option_track_pillars = tkinter.BooleanVar()
    option_track_pillars.set(True)
    c1 = tkinter.Checkbutton(window, text='Track Pillars', variable=option_track_pillars, onvalue=True, offvalue=False)
    c1.pack()

    # Menu for Code Sections to run
    # Create checkbox
    option_section2 = tkinter.BooleanVar()
    option_section3 = tkinter.BooleanVar()
    option_section4 = tkinter.BooleanVar()

    option_section2.set(True)
    option_section3.set(True)
    option_section4.set(True)

    s2 = tkinter.Checkbutton(window, text='Sort and Arrange Files', variable=option_section2, onvalue=True,
                             offvalue=False)

    s3 = tkinter.Checkbutton(window, text='Run parallel woundcomputes', variable=option_section3, onvalue=True,
                             offvalue=False)
    s4 = tkinter.Checkbutton(window, text='Run extract_data', variable=option_section4, onvalue=True,
                             offvalue=False)

    s2.pack()
    s3.pack()
    s4.pack()

    # Create button to accept variables inputed
    tkinter.Button(window, text="Proceed", command=accept).pack()
    tkinter.Button(window, text="Quit", command=killmenow).pack()
    # Execute tkinter
    window.mainloop()

    return image_type_clicked.get(), option_track_pillars.get(), parallel_processes_clicked.get(), microscope_type_clicked.get(), option_section2.get(), option_section3.get(), option_section4.get()


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
                if ms_choice == "Cytation":
                    spos = file.split('_')[0][:1] + file.split('_')[0][1:].zfill(2)
                else:
                    spos = file.split('_')[-2][:1] + file.split('_')[-2][1:].zfill(2)
                    if verbose:
                        print("spos: ", spos)
                if is_nd:
                    spos = spos + '_' + stage_pos_maps_fn[basename_fn][int(spos.split('s')[-1])]
                    if verbose:
                        print('spos_nd:', spos)

                path_input_fn = os.path.join(parent_output_fn, basename_fn)
                path_pos_output_fn = os.path.join(parent_output_fn, basename_fn, spos)

                # Isolate the frame number (timepoint)
                if ms_choice == "Cytation":
                    file_timepoint = file.split('_')[-1].split('.')[0]
                    if file_timepoint.isdigit():
                        file_newname = spos + '_t' + file_timepoint + '.TIF'
                    else:
                        file_newname = spos + '.TIF'
                else:
                    try:
                        file_timepoint = file.casefold().split('_t')[-1].split('.')[0]
                        # Rename file for correct time and stage position sort syntax (_sXX_ and _tXXX.)
                    except ValueError:
                        file_newname = spos + '.TIF'
                    else:
                        file_newname = spos + '_t' + file_timepoint.zfill(3) + '.TIF'
                    if verbose:
                        print("file_newname: ", file_newname)

                # check if stage position directory already exists and move file into this folder if it does
                if os.path.exists(os.path.join(path_pos_output_fn, image_type_fn + '_images')):
                    try:
                        shutil.move(os.path.join(path_input_fn, file),
                                    os.path.join(path_pos_output_fn, image_type_fn + '_images', file_newname))
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
                                    os.path.join(path_pos_output_fn, image_type_fn + '_images', file_newname))
                        if verbose:
                            print("moving file:", file)


                    except OSError as e:
                        # If it fails, inform the user.
                        print('Error: %s - %s.' % (e.filename, e.strerror))


def sort_parallel_processes(basename_list_fn: list, parent_output_fn: str, parallels_in: int, is_nd: bool):
    """Given basename list, parent output folder, number of stage positions list, number of parallel processes. Sorts 
    tissues into subfolders for parallel processing"""
    # Create processing folders
    for index_fn, basename_fn in enumerate(basename_list_fn):
        path_input_fn = os.path.join(parent_output_fn, basename_fn)
        file_list = os.listdir(path_input_fn)
        file_list.sort()
        if is_nd:
            file_list = [n1 for n1 in file_list if not n1.endswith('.nd')]

        for p_folder in range(1, parallels_in + 1):
            loc_p_folder = os.path.join(path_input_fn, 'p' + f"{p_folder:02}")
            stage_pos_start = (p_folder - 1) * int(round((len(file_list) + 1) / parallels_in))
            stage_pos_end = p_folder * int(round((len(file_list) + 1) / parallels_in))
            if stage_pos_end > len(file_list):
                stage_pos_end = len(file_list)
            try:
                os.makedirs(loc_p_folder)
                for stage_pos_fn in range(stage_pos_start, stage_pos_end):
                    # define input and output paths
                    move_loc_from = os.path.join(path_input_fn, file_list[stage_pos_fn])
                    move_loc_to = os.path.join(loc_p_folder, file_list[stage_pos_fn])
                    try:
                        shutil.move(move_loc_from, move_loc_to)
                    except OSError as e:
                        # If it fails, inform the user.
                        print('Error: %s - %s.' % (e.filename, e.strerror))
            except OSError as e:
                # If it fails, inform the user.
                print('Error: %s - %s.' % (e.filename, e.strerror))

        stage_pos_max = parallels_in * int(round((len(file_list) + 1) / parallels_in))

        if stage_pos_max < len(file_list):
            for stage_pos_fn in range(stage_pos_max, len(file_list)):
                # define input and output paths
                move_loc_from = os.path.join(path_input_fn, file_list[stage_pos_fn])
                move_loc_to = os.path.join(loc_p_folder, file_list[stage_pos_fn])
                try:
                    shutil.move(move_loc_from, move_loc_to)
                except OSError as e:
                    # If it fails, inform the user.
                    print('Error: %s - %s.' % (e.filename, e.strerror))


# WoundCompute Functions
def run_threads(script_name_fn, path_input_fn):
    subprocess.run(["python", script_name_fn, path_input_fn])


def woundcompute_run_Eclipse_Ti(input_path_fn: str):
    # ** Section 3: Execute woundcompute for all basename folders in the Sorted folder ** #

    time_all = []
    for subfolder in os.listdir(input_path_fn):
        position = Path(input_path_fn).joinpath(subfolder)
        current = time.time()
        try:
            time_all, action_all = ia.run_all(position)
            secondsPassed = time.time() - current
            print("Thread: ", os.path.basename(os.path.normpath(input_path_fn)), "tissue: ", subfolder, "time: ",
                  format_timespan(secondsPassed))
        except Exception as ex:
            time_all.append(time.time())
            print("Thread: ", os.path.basename(os.path.normpath(input_path_fn)), " tissue: ", subfolder, " time: ",
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



