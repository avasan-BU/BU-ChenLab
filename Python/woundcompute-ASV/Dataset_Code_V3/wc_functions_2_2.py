# Name: wc_functions
#
# Version: 2.2
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
import time
from humanfriendly import format_timespan
from woundcompute import image_analysis as ia
from pathlib import Path
import sys

# GUI Functions
def io_function() -> (str, str):
    """Prompt user for input folder that contains a .nd file"""
    # prompt user for the file directory. Will open as a popup window named "tk"
    tk_root = tkinter.Tk()
    print("Please open the directory that contains your .nd file")
    path_input = askdirectory(title='Select Input Folder with .nd file')  # shows dialog box and return the path
    print("Inputed path:", path_input)
    tk_root.destroy()
    path_output = path_input + '/Sorted'

    if os.path.exists(path_output):
        path_out_new = input('Enter new output folder name')
        path_output = path_input + '/' + path_out_new
        os.makedirs(path_output)
    # create a new  output directory
    else:
        os.makedirs(path_output)

    print(path_output)
    print(path_input)
    return path_input, path_output


def input_gui() -> (str, bool, int, str):
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

    parallel_processes_clicked = tkinter.IntVar(value=7)

    # Create Label
    label_parallel_processes = tkinter.Label(window, text="Number of Parallel Processes:")
    label_parallel_processes.pack()

    # Create Dropdown menu
    scale = tkinter.Scale(window, from_=1, to=12, orient="horizontal", variable=parallel_processes_clicked)
    scale.pack(side="top", fill="x")

    # Menu for Pillar Tracking
    # Create checkbox
    option_track_pillars = tkinter.BooleanVar()
    c1 = tkinter.Checkbutton(window, text='Track Pillars', variable=option_track_pillars, onvalue=True, offvalue=False)
    c1.pack()

    # Menu for Code Sections to run
    # Create checkbox
    # option_section2 = tkinter.BooleanVar()
    # option_section3 = tkinter.BooleanVar()
    #
    # s2 = tkinter.Checkbutton(window, text='Sort and Arrange Files', variable=option_section2, onvalue=True, offvalue=False)
    #
    # s3 = tkinter.Checkbutton(window, text='Run parallel woundcomputes', variable=option_section3, onvalue=True, offvalue=False)
    #
    # s2.pack()
    # s3.pack()

    # Create button to accept variables inputed
    tkinter.Button(window, text="Proceed", command=accept).pack()
    tkinter.Button(window, text="Quit", command=killmenow).pack()
    # Execute tkinter
    window.mainloop()

    return image_type_clicked.get(), option_track_pillars.get(), parallel_processes_clicked.get(), microscope_type_clicked.get(), option_section2.get(),option_section3.get()


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
    with open(path + '/wc_dataset_' + image_type_in + '.yaml', 'w') as file:
        yaml.safe_dump(yaml_input_file, file, sort_keys=False)


def define_basename_list(path_input_fn: str) -> list:
    """Given an input path as a string. Will return a list of experiment names in the input folder"""

    basename_list_fn = []
    for file in os.listdir(path_input_fn):
        if file.endswith('.nd'):
            name, ext = os.path.splitext(file)
            basename_list_fn.append(name)
    return basename_list_fn


def extract_nd_info(basename_list_fn: list, path_output_fn: str) -> list:
    """Given a basename list and an output path. Will extract number of stage positions for each list and create
    position map lists for each basename"""

    stage_positions = []
    stage_pos_maps = []
    for index_fn, basename_fn in enumerate(basename_list_fn):
        with open(path_output_fn + '/' + basename_fn + '/' + basename_fn + '.nd', 'r') as nd_file:
            for l_no, line in enumerate(nd_file):
                if '"NStagePositions"' in line:
                    stage_positions.append([int(s) for s in line.split() if s.isdigit()][-1])
                    break

    return stage_positions


# Folder Organization Functions
def sort_basename_folders(basename_list_fn: list, path_input_fn: str, path_output_fn: str):
    """Given a list of experiments obtained from the .nd files in the input folder. Given input and out paths as str.
 Creates an output folder at path_output. Copies and sorts TIFF files in path_input according to basenames in output
 folder"""

    for basename_fn in basename_list_fn:

        # create folders for each expt
        os.makedirs(path_output_fn + '/' + basename_fn)

        # copy .nd file into respective basename folder
        shutil.copy(path_input_fn + '/' + basename_fn + '.nd',
                    path_output_fn + '/' + basename_fn + '/' + basename_fn + '.nd')

        # copy TIF files to respective basename folders, excludes thumbnail files
        for file in os.listdir(path_input_fn):
            if file.startswith(basename_fn + '_') and not fnmatch.fnmatch(file, '*thumb*'):
                shutil.copy(path_input_fn + '/' + file, path_output_fn + '/' + basename_fn + '/' + file)


def sort_stage_pos_folders(basename_list_fn: list, parent_output_fn: str, stage_pos_nd_fn: list, image_type_fn: str):
    """Given basename list, parent output folder and number of stage positions list extracted from nd files. Sorts
    files into stage position folders"""
    # sort images into stage position folders
    for index_fn, basename_fn in enumerate(basename_list_fn):

        for file in os.listdir(parent_output_fn + '/' + basename_fn):

            for stage_pos_fn in range(1, stage_pos_nd_fn[index_fn] + 1):

                # define input and output paths
                path_input_fn = parent_output_fn + '/' + basename_fn
                path_pos_output_fn = parent_output_fn + '/' + basename_fn + '/' + 's' + f"{stage_pos_fn:02}"

                # check if file belongs to current stage_pos group
                if fnmatch.fnmatch(file, '*s%i' % stage_pos_fn + '_*'):

                    # rename file for correct stage position sort syntax (_sXX_)

                    # Isolate the frame number (timepoint)
                    file_timepoint = file.split('_t', 1)[-1].split('.', 1)[0]
                    # Rename file for correct time and stage position sort syntax (_sXX_ and _tXXX.)
                    file_newname = 's' + f"{stage_pos_fn:02}" + '_t' + f"{int(file_timepoint):03}" + '.TIF'

                    # check if stage position directory already exists and move file into this folder if it does
                    if os.path.exists(path_pos_output_fn + '/' + image_type_fn + '_images/'):
                        try:
                            shutil.move(path_input_fn + '/' + file,
                                        path_pos_output_fn + '/' + image_type_fn + '_images/' + file_newname)
                        except OSError as e:
                            # If it fails, inform the user.
                            print('Error: %s - %s.' % (e.filename, e.strerror))
                    # otherwise, create folder and move file into this folder. Also copy parent yaml file into this folder.
                    else:
                        try:
                            os.makedirs(path_pos_output_fn + '/' + image_type_fn + '_images/')
                            shutil.copy(parent_output_fn + '/wc_dataset_' + image_type_fn + '.yaml',
                                        path_pos_output_fn + '/wc_dataset_' + image_type_fn + '.yaml')
                            shutil.move(path_input_fn + '/' + file,
                                        path_pos_output_fn + '/' + image_type_fn + '_images/' + file_newname)


                        except OSError as e:
                            # If it fails, inform the user.
                            print('Error: %s - %s.' % (e.filename, e.strerror))

                elif fnmatch.fnmatch(file, '*s%i' % stage_pos_fn + '.TIF'):

                    # If data does not have timepoints, rename stage positions only for correct sort syntax
                    file_newname = 's' + f"{stage_pos_fn:02}" + '.TIF'

                    # check if stage position directory already exists and move file into this folder if it does
                    if os.path.exists(path_pos_output_fn + '/' + image_type_fn + '_images/'):
                        try:
                            shutil.move(path_input_fn + '/' + file,
                                        path_pos_output_fn + '/' + image_type_fn + '_images/' + file_newname)
                        except OSError as e:
                            # If it fails, inform the user.
                            print('Error: %s - %s.' % (e.filename, e.strerror))
                    # otherwise, create folder and move file into this folder. Also copy parent yaml file into this folder.
                    else:
                        try:
                            os.makedirs(path_pos_output_fn + '/' + image_type_fn + '_images/')
                            shutil.copy(parent_output_fn + '/wc_dataset_' + image_type_fn + '.yaml',
                                        path_pos_output_fn + '/wc_dataset_' + image_type_fn + '.yaml')
                            shutil.move(path_input_fn + '/' + file,
                                        path_pos_output_fn + '/' + image_type_fn + '_images/' + file_newname)


                        except OSError as e:
                            # If it fails, inform the user.
                            print('Error: %s - %s.' % (e.filename, e.strerror))


def sort_parallel_processes(basename_list_fn: list, parent_output_fn: str, stage_pos_nd_fn: list, image_type_fn: str,
                            parallels_in: int):
    """Given basename list, parent output folder, number of stage positions list, number of parallel processes. Sorts 
    tissues into subfolders for parallel processing"""
    # Create processing folders
    for index_fn, basename_fn in enumerate(basename_list_fn):
        path_input_fn = parent_output_fn + '/' + basename_fn
        stage_pos_max = parallels_in * int(round((stage_pos_nd_fn[index_fn] + 1) / parallels_in)) + 1
        for p_folder in range(1, parallels_in + 1):
            loc_p_folder = path_input_fn + '/' + 'p' + f"{p_folder:02}"
            stage_pos_start = (p_folder - 1) * int(round((stage_pos_nd_fn[index_fn] + 1) / parallels_in)) + 1
            stage_pos_end = p_folder * int(round((stage_pos_nd_fn[index_fn] + 1) / parallels_in)) + 1
            if stage_pos_end > stage_pos_nd_fn[index_fn]:
                stage_pos_end = stage_pos_nd_fn[index_fn]
            try:
                os.makedirs(loc_p_folder)
                for stage_pos_fn in range(stage_pos_start, stage_pos_end):
                    # define input and output paths
                    move_loc_from = path_input_fn + '/' + 's' + f"{stage_pos_fn:02}"
                    move_loc_to = loc_p_folder + '/' + 's' + f"{stage_pos_fn:02}"
                    try:
                        shutil.move(move_loc_from, move_loc_to)
                    except OSError as e:
                        # If it fails, inform the user.
                        print('Error: %s - %s.' % (e.filename, e.strerror))
            except OSError as e:
                # If it fails, inform the user.
                print('Error: %s - %s.' % (e.filename, e.strerror))

        if stage_pos_max < stage_pos_nd_fn[index_fn] + 1:
            loc_p_folder = path_input_fn + '/' + 'p' + f"{parallels_in:02}"
            for stage_pos_fn in range(stage_pos_max, stage_pos_nd_fn[index_fn] + 1):
                # define input and output paths
                move_loc_from = path_input_fn + '/' + 's' + f"{stage_pos_fn:02}"
                move_loc_to = loc_p_folder + '/' + 's' + f"{stage_pos_fn:02}"
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

