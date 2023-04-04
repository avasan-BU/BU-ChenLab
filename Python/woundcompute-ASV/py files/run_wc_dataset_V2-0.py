#!/usr/bin/env python
# coding: utf-8

# Name: run_wc_dataset;
# 
# Version: 2.0;
# 
# Author: Anish Vasan;
# 
# Organization: Chen/Eyckmans Lab, Boston University;
# 
# Date: 20230403;

# ## IMPORTS ##

# In[ ]:


import os, shutil, fnmatch, tkinter, yaml
from tkinter.filedialog import askdirectory
from pathlib import Path
from woundcompute import image_analysis as ia
import time
import os, shutil, fnmatch, tkinter, yaml
from tkinter.filedialog import askdirectory
from pathlib import Path
from woundcompute import image_analysis as ia
import time


# ## DEFINITIONS ##
# ## These require user input/changes based on experiments ##

# In[ ]:


image_type = "ph1"  #Options:  bf, ph1
is_fl = False #Options: True, False
is_track = False #Options: True, False


# ## FUNCTIONS ##

# In[ ]:


def create_yaml(path_output: str, image_type: str):
    """Given the output path as string. Will create a yaml file in the main output folder. This yaml file will be copied into each subfolder during the sorting function"""

    #Default keys and values stored in yaml file
    yaml_input_file = {
    'version' : 1.0,
    'segment_brightfield' : False,
    'seg_bf_version' : 1,
    'seg_bf_visualize' : False,
    'segment_fluorescent' : False,
    'seg_fl_version' : 1,
    'seg_fl_visualize' : False,
    'segment_ph1' : False, #True,
    'seg_ph1_version' : 2,
    'seg_ph1_visualize' : False, #True,
    'track_brightfield' : False,
    'track_bf_version' : 1,
    'track_bf_visualize' : False,
    'track_ph1' : False,
    'track_ph1_version' : 1,
    'track_ph1_visualize' : False,
    'bf_seg_with_fl_seg_visualize' : False,
    'bf_track_with_fl_seg_visualize' : False,
    'ph1_seg_with_fl_seg_visualize' : False,
    'ph1_track_with_fl_seg_visualize' : False,
    }

    #Conditionally modify yaml file based on image_type input

    for key, value in yaml_input_file.items():
        if image_type in key and not "version" in key and not "fl" in key and not "track" in key:
            yaml_input_file[key] = True

            if is_fl:
                if "fl" in key and not "version" in key:
                    yaml_input_file[key] = True

            if is_track:
                if "track" in key and not "version" in key:
                    yaml_input_file[key] = True

    # Write yaml output to path_output
    with open(path_output+'/wc_dataset_'+image_type+'.yaml', 'w') as file:
        yaml.safe_dump(yaml_input_file, file, sort_keys=False)


# In[ ]:


def define_basename_list(path_input: str) -> list:
    """Given an input path as a string. Will return a list of experiment names in the input folder"""

    basename_list = []
    for file in os.listdir(path_input):
        if file.endswith('.nd'):
            name, ext = os.path.splitext(file)
            basename_list.append(name)
    return basename_list


# In[ ]:


def sort_basename_folders(basename_list: list, path_input: str, path_output: str):
    """Given a list of experiments obtained from the .nd files in the input folder. Given input and out paths as str. Creates an output folder at path_output. Copies and sorts TIFF files in path_input according to basenames in output folder """

    for basename in basename_list:

        #create folders for each expt
        os.makedirs(path_output + '/' + basename)

        #copy .nd file into respective basename folder
        shutil.copy(path_input + '/' + basename + '.nd', path_output + '/' + basename + '/' + basename + '.nd')

        #copy TIF files to respective basename folders, excludes thumbnail files
        for file in os.listdir(path_input):
            if file.startswith(basename + '_') and not fnmatch.fnmatch(file, '*thumb*'):
                shutil.copy(path_input + '/' + file, path_output + '/' + basename + '/' + file)


# In[ ]:


def extract_nd_info(basename_list: list,path_output: str)-> list:
    """Given a basename list and an output path. Will extract number of stage positions for each list and create position map lists for each basename"""

    stage_positions = []
    for basename in basename_list:
        with open(path_output + '/' + basename + '/' + basename + '.nd', 'r') as nd_file:
            for l_no, line in enumerate(nd_file):
                if '"NStagePositions"' in line:
                    stage_positions.append([int(s) for s in line.split() if s.isdigit()][-1])
                    break

    return stage_positions


# In[ ]:


def sort_stage_pos_folders(basename_list: list,parent_output: str, stage_pos_nd: list, image_type: str):
    """Given basename list, parent output folder and number of stage positions list extracted from nd files. Sorts files into stage position folders"""
    #sort images into stage position folders
    for index,basename in enumerate(basename_list):

        for file in os.listdir(parent_output+'/'+basename):
            for stage_pos in range(1,stage_pos_nd[index]+1):

                #define input and output paths
                path_input  = parent_output + '/' + basename
                path_pos_output =  parent_output + '/' + basename + '/' + 's' + f"{stage_pos:02}"


                #check if file belongs to current stage_pos group
                if fnmatch.fnmatch(file, '*s%i' % stage_pos+'_*'):

                #rename file for correct stage position sort syntax (_sXX_)
                    # check if data has timepoints
                    if fnmatch.fnmatch(file, '*_t*'):

                        #Isolate the frame number (timepoint)
                        file_timepoint = file.split('_t', 1)[-1].split('.', 1)[0]
                        # Rename file for correct time and stage position sort syntax (_sXX_ and _tXXX.)
                        file_newname = 's' + f"{stage_pos:02}" +'_t'+f"{int(file_timepoint):03}"+'.TIF'

                    else:

                        #If data does not have timepoints, rename stage positions only for correct sort syntax
                        file_newname = 's' + f"{stage_pos:02}" + '.TIF'

                    #check if stage position directory already exists and move file into this folder if it does
                    if os.path.exists(path_pos_output + '/' + image_type+ '_images/'):
                        try:
                            shutil.move(path_input + '/' + file, path_pos_output + '/' + image_type+ '_images/'+ file_newname)
                        except OSError as e:
                            # If it fails, inform the user.
                            print('Error: %s - %s.' % (e.filename, e.strerror))
                    #otherwise, create folder and move file into this folder. Also copy parent yaml file into this folder.
                    else:
                        try:
                            os.makedirs(path_pos_output + '/' + image_type+ '_images/')
                            shutil.copy(parent_output + '/wc_dataset_'+image_type+'.yaml', path_pos_output + '/wc_dataset_'+image_type+'.yaml')
                            shutil.move(path_input + '/' + file, path_pos_output + '/' + image_type+ '_images/'+ file_newname)


                        except OSError as e:
                            # If it fails, inform the user.
                            print('Error: %s - %s.' % (e.filename, e.strerror))


# ## RUN CODE ##
# 
# **Section 1: Navigate to data folder containing .nd file**

# In[ ]:


#prompt user for the file directory. Will open as a popup window named "tk"
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
#create a new  output directory
else:
    os.makedirs(path_output)


# **Section 2: Execute functions to prepare folder structure for woundcompute**

# In[ ]:


# Create yaml file for image type
create_yaml(path_output, image_type)

# Create list of .nd files/experiments in the input folder
basename_list = define_basename_list(path_input)

# Sort images in input folder into Sorted/basename folder
sort_basename_folders(basename_list, path_input, path_output)

# Extract stage position information from .nd file
stage_pos_nd = extract_nd_info(basename_list,path_output)

#  Sort images in each basename folder into their corresponding stage position folders
sort_stage_pos_folders(basename_list,path_output, stage_pos_nd, image_type)


# **Section 3: Execute woundcompute for all basename folders in the Sorted folder**

# In[ ]:


for index, basename in enumerate(basename_list):

    for stage_pos in range(1, stage_pos_nd[index]+1):
        input_location = Path(path_output+'/'+basename+'/'+'s' + f"{stage_pos:02}")
        try:
            time_all, action_all = ia.run_all(input_location)
            print("tissue number:", stage_pos, "time:", time.time())
        except Exception as ex:
            time_all.append(time.time())
            print("tissue number:", stage_pos, "time:", time.time())
            print("---------ERROR OF SOME DESCRIPTION HAS HAPPENED-------")
            print(ex)
            print("------------------------------------------------------")

