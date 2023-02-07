#!/usr/bin/env python
# coding: utf-8

# In[15]:


#imports
import os, shutil, time, tkinter
from tkinter.filedialog import askdirectory
from pathlib import Path
from woundcompute import image_analysis as ia


# In[24]:


#prompt user for the file directory. Will open as a popup window named "tk"
tk_root = tkinter.Tk()
path_input = askdirectory(title='Select Input Folder')  # shows dialog box and return the path
print(path_input)
tk_root.destroy()

tk_root = tkinter.Tk()
path_output = askdirectory(title='Select Output Folder')  # shows dialog box and return the path
print(path_output)
tk_root.destroy()


# In[25]:


#Copy TIF files into folders grouped by plate position
for file in os.listdir(path_input):
    #Check if position described with only 2 characters
    if file[2] == '_':
        if os.path.exists(path_output + '/' + file[:2] + '/ph1_images'):
            try:
                shutil.copy(path_input + '/' + file, path_output + '/' + file[:2] + '/ph1_images/' + file)
            except OSError as e:
                # If it fails, inform the user.
                print('Error: %s - %s.' % (e.filename, e.strerror))

        else:
            try:
                os.makedirs(path_output + '/' + file[:2] + '/ph1_images')
                shutil.copy('G:/My Drive/Boston University/Chen Lab/Code/Anish/wc_dataset_ph1.yaml',
                            path_output + '/' + file[:2] + '/wc_dataset_ph1.yaml')
                shutil.copy(path_input + '/' + file, path_output + '/' + file[:2] + '/ph1_images/' + file)

            except OSError as e:
                # If it fails, inform the user.
                print('Error: %s - %s.' % (e.filename, e.strerror))

    #Otherwise, assume position is described with 3 characters
    else:
        if os.path.exists(path_output + '/' + file[:3] + '/ph1_images'):
            try:
                shutil.copy(path_input + '/' + file, path_output + '/' + file[:3] + '/ph1_images/' + file)
            except OSError as e:
                # If it fails, inform the user.
                print('Error: %s - %s.' % (e.filename, e.strerror))

        else:
            try:
                os.makedirs(path_output + '/' + file[:3] + '/ph1_images')
                shutil.copy('G:/My Drive/Boston University/Chen Lab/Code/Anish/wc_dataset_ph1.yaml',
                            path_output + '/' + file[:3] + '/ph1_images/wc_dataset_ph1.yaml')
                shutil.copy(path_input + '/' + file, path_output + '/' + file[:3] + '/ph1_images/' + file)

            except OSError as e:
                # If it fails, inform the user.
                print('Error: %s - %s.' % (e.filename, e.strerror))


# In[ ]:


#run wound compute code for all plate positions
for folder in os.listdir(path_output):
    input_location = Path(path_output + '/' + folder)
    try:
        time_all, action_all = ia.run_all(input_location)
        print("tissue number:", stage_pos, "time:", time.time())
    except Exception as ex:
        time_all.append(time.time())
        print("tissue number:", stage_pos, "time:", time.time())
        print("---------ERROR OF SOME DESCRIPTION HAS HAPPENED-------")
        print(ex)
        print("------------------------------------------------------")

