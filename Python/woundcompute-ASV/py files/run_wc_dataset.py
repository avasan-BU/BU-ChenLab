#!/usr/bin/env python
# coding: utf-8

# In[13]:


#imports
import os, shutil, fnmatch, time, tkinter
from tkinter.filedialog import askdirectory
from pathlib import Path
from woundcompute import image_analysis as ia


# 

# In[14]:


#prompt user for the file directory. Will open as a popup window named "tk"
tk_root = tkinter.Tk()
path_input = askdirectory(title='Select Folder')  # shows dialog box and return the path
print(path_input)
tk_root.destroy()
path_output = path_input + '/Sorted'

if os.path.exists(path_output):
    path_out_new = input('Enter new output folder name')
    path_output = path_input + '/' + path_out_new
    os.makedirs(path_output)
#create a new  output directory
else:
    os.makedirs(path_output)


# In[15]:


#find the experiment base names based on the .nd files in the folder
basename_list = []
for file in os.listdir(path_input):
    if file.endswith('.nd'):
        name, ext = os.path.splitext(file)
        basename_list.append(name)
        #create folders for each expt
        os.makedirs(path_output + '/' + name)
print(basename_list)


# In[16]:


#copy files into folders grouped by expt base names
stage_pos_nd = []
for basename in basename_list:

    #copy .nd file into respective basename folder
    shutil.copy(path_input + '/' + basename + '.nd', path_output + '/' + basename + '/' + basename + '.nd')
    with open(path_output + '/' + basename + '/' + basename + '.nd', 'r') as nd_file:
        for l_no, line in enumerate(nd_file):
            if '"NStagePositions"' in line:
                stage_pos_nd.append([int(s) for s in line.split() if s.isdigit()][-1])
                break
    #copy TIF files to respective basename folders
    for file in os.listdir(path_input):
        if file.startswith(basename + '_'):
            shutil.copy(path_input + '/' + file, path_output + '/' + basename + '/' + file)


# In[ ]:


#delete thumbnail files in folder
for basename in basename_list:
    for file in os.listdir(path_output + '/' + basename):
        if fnmatch.fnmatch(file, '*thumb*'):
            # Delete the thumbnail files - with exception handling
            try:
                os.remove(path_output + '/' + basename + '/' + file)
            except OSError as e:
                # If it fails, inform the user.
                print('Error: %s - %s.' % (e.filename, e.strerror))#%%
#imports
import os, shutil, fnmatch, time, tkinter
from tkinter.filedialog import askdirectory
from pathlib import Path
from woundcompute import image_analysis as ia


# 

# In[ ]:


#prompt user for the file directory. Will open as a popup window named "tk"
tk_root = tkinter.Tk()
path_input = askdirectory(title='Select Folder')  # shows dialog box and return the path
print(path_input)
tk_root.destroy()
path_output = path_input + '/Sorted'

if os.path.exists(path_output):
    path_out_new = input('Enter new output folder name')
    path_output = path_input + '/' + path_out_new
    os.makedirs(path_output)
#create a new  output directory
else:
    os.makedirs(path_output)


# In[ ]:


#find the experiment base names based on the .nd files in the folder
basename_list = []
for file in os.listdir(path_input):
    if file.endswith('.nd'):
        name, ext = os.path.splitext(file)
        basename_list.append(name)
        #create folders for each expt
        os.makedirs(path_output + '/' + name)
print(basename_list)


# In[ ]:


#copy files into folders grouped by expt base names
stage_pos_nd = []
for basename in basename_list:

    #copy .nd file into respective basename folder
    shutil.copy(path_input + '/' + basename + '.nd', path_output + '/' + basename + '/' + basename + '.nd')
    with open(path_output + '/' + basename + '/' + basename + '.nd', 'r') as nd_file:
        for l_no, line in enumerate(nd_file):
            if '"NStagePositions"' in line:
                stage_pos_nd.append([int(s) for s in line.split() if s.isdigit()][-1])
                break
    #copy TIF files to respective basename folders
    for file in os.listdir(path_input):
        if file.startswith(basename + '_'):
            shutil.copy(path_input + '/' + file, path_output + '/' + basename + '/' + file)


# In[ ]:


#delete thumbnail files in folder
for basename in basename_list:
    for file in os.listdir(path_output + '/' + basename):
        if fnmatch.fnmatch(file, '*thumb*'):
            # Delete the thumbnail files - with exception handling
            try:
                os.remove(path_output + '/' + basename + '/' + file)
            except OSError as e:
                # If it fails, inform the user.
                print('Error: %s - %s.' % (e.filename, e.strerror))


# In[ ]:


#sort images into stage position folders
for index,basename in enumerate(basename_list):

    for file in os.listdir(path_output+'/'+basename):
        for stage_pos in range(1,stage_pos_nd[index]+1):

            #check if file belongs to current stage_pos group
            if fnmatch.fnmatch(file, '*s%i' % stage_pos+'_*'):

                #rename file for correct sort syntax
                file_timepoint = file.split('_t', 1)[-1].split('.', 1)[0]

                for num in range(3-len(file_timepoint)):
                    file_timepoint = '0'+file_timepoint
                filename_new = 's%i' % stage_pos+'_t'+file_timepoint+'.TIF'

                #check if stage position directory already exists and move file into this folder if it does
                if os.path.exists(path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images'):
                    try:
                        shutil.move(path_output+'/'+basename+'/'+file, path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images/'+filename_new)
                    except OSError as e:
                        # If it fails, inform the user.
                        print('Error: %s - %s.' % (e.filename, e.strerror))

                else:
                    try:
                        os.makedirs(path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images')
                        shutil.copy('G:/My Drive/Boston University/Chen Lab/Code/Anish/wc_dataset_ph1.yaml', path_output+'/'+basename+'/'+'s%i' % stage_pos+'/wc_dataset_ph1.yaml')
                        shutil.move(path_output+'/'+basename+'/'+file, path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images/'+filename_new)

                    except OSError as e:
                        # If it fails, inform the user.
                        print('Error: %s - %s.' % (e.filename, e.strerror))
            elif fnmatch.fnmatch(file, '*s%i' % stage_pos+'.TIF'):
                if os.path.exists(path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images'):
                    try:
                        shutil.move(path_output+'/'+basename+'/'+file, path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images/'+file)
                    except OSError as e:
                        # If it fails, inform the user.
                        print('Error: %s - %s.' % (e.filename, e.strerror))
                # if the directory does not already exist, create directory and move file into it
                else:
                    try:
                        os.makedirs(path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images')
                        shutil.copy('G:/My Drive/Boston University/Chen Lab/Code/Anish/wc_dataset_ph1.yaml', path_output+'/'+basename+'/'+'s%i' % stage_pos+'/wc_dataset_ph1.yaml')
                        shutil.move(path_output+'/'+basename+'/'+file, path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images/'+file)

                    except OSError as e:
                        # If it fails, inform the user.
                        print('Error: %s - %s.' % (e.filename, e.strerror))


# In[ ]:


for index, basename in enumerate(basename_list):

    for stage_pos in range(1, stage_pos_nd[index]+1):
        input_location = Path(path_output+'/'+basename+'/'+'s%i' % stage_pos)
        try:
            time_all, action_all = ia.run_all(input_location)
            print("tissue number:", stage_pos, "time:", time.time())
        except Exception as ex:
            time_all.append(time.time())
            print("tissue number:", stage_pos, "time:", time.time())
            print("---------ERROR OF SOME DESCRIPTION HAS HAPPENED-------")
            print(ex)
            print("------------------------------------------------------")#%%
#sort images into stage position folders
for index,basename in enumerate(basename_list):

    for file in os.listdir(path_output+'/'+basename):
        for stage_pos in range(1,stage_pos_nd[index]+1):
            
            #check if file belongs to current stage_pos group
            if fnmatch.fnmatch(file, '*s%i' % stage_pos+'_*'):

                #rename file for correct sort syntax
                file_timepoint = file.split('_t', 1)[-1].split('.', 1)[0]

                for num in range(3-len(file_timepoint)):
                    file_timepoint = '0'+file_timepoint 
                filename_new = 's%i' % stage_pos+'_t'+file_timepoint+'.TIF'

                #check if stage position directory already exists and move file into this folder if it does
                if os.path.exists(path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images'):
                    try:
                        shutil.move(path_output+'/'+basename+'/'+file, path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images/'+filename_new)
                    except OSError as e:
                        # If it fails, inform the user.
                        print('Error: %s - %s.' % (e.filename, e.strerror))

                else:
                    try:
                        os.makedirs(path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images')
                        shutil.copy('G:/My Drive/Boston University/Chen Lab/Code/Anish/wc_dataset_ph1.yaml', path_output+'/'+basename+'/'+'s%i' % stage_pos+'/wc_dataset_ph1.yaml')
                        shutil.move(path_output+'/'+basename+'/'+file, path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images/'+filename_new)

                    except OSError as e:
                        # If it fails, inform the user.
                        print('Error: %s - %s.' % (e.filename, e.strerror))
            elif fnmatch.fnmatch(file, '*s%i' % stage_pos+'.TIF'):
                if os.path.exists(path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images'):
                    try:
                        shutil.move(path_output+'/'+basename+'/'+file, path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images/'+file)
                    except OSError as e:
                        # If it fails, inform the user.
                        print('Error: %s - %s.' % (e.filename, e.strerror))
                # if the directory does not already exist, create directory and move file into it
                else:
                    try:
                        os.makedirs(path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images')
                        shutil.copy('G:/My Drive/Boston University/Chen Lab/Code/Anish/wc_dataset_ph1.yaml', path_output+'/'+basename+'/'+'s%i' % stage_pos+'/wc_dataset_ph1.yaml')
                        shutil.move(path_output+'/'+basename+'/'+file, path_output+'/'+basename+'/'+'s%i' % stage_pos+'/ph1_images/'+file)
                        
                    except OSError as e:
                        # If it fails, inform the user.
                        print('Error: %s - %s.' % (e.filename, e.strerror))


# In[ ]:


for index, basename in enumerate(basename_list):
    
    for stage_pos in range(1, stage_pos_nd[index]+1):
        input_location = Path(path_output+'/'+basename+'/'+'s%i' % stage_pos)
        try:
            time_all, action_all = ia.run_all(input_location)
            print("tissue number:", stage_pos, "time:", time.time())
        except Exception as ex:
            time_all.append(time.time())
            print("tissue number:", stage_pos, "time:", time.time())
            print("---------ERROR OF SOME DESCRIPTION HAS HAPPENED-------")
            print(ex)
            print("------------------------------------------------------")

