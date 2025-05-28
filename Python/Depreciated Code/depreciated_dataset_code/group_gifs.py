#!/usr/bin/env python
# coding: utf-8

# In[6]:


#imports
import os, shutil, tkinter
from tkinter.filedialog import askdirectory

import matplotlib.pyplot as plt

from PIL import Image


# In[7]:


#prompt user for the file directory. Will open as a popup window named "tk"
tk_root = tkinter.Tk()
path_input = askdirectory(title='Select Folder')  # shows dialog box and return the path
print(path_input)
tk_root.destroy()


# In[8]:


stage_pos_chars = []
for file in os.listdir(path_input):
    if file.endswith('.nd'):
        basename = file.split('.',1)[0]
        with open(path_input + '/' +file, 'r') as nd_file:
            for l_no, line in enumerate(nd_file):
                if '"NStagePositions"' in line:
                    stage_pos_nd = [int(s) for s in line.split() if s.isdigit()][-1]
                if '"NTimePoints"' in line:
                    timepoints_nd = [int(s) for s in line.split() if s.isdigit()][-1]
                if '"Stage' in line:
                    spc = line.split(', "')[-1]
                    stage_pos_chars.append(spc[0:len(spc)-2])


# In[9]:


list_pos= []
tlist = [T*0.5 for T in range(1,timepoints_nd+1)]
for file in os.listdir(path_input):
    if os.path.isdir(path_input+'/'+file):
        list_pos.append(file)
        if os.path.exists(path_input + '/GIFs'):
            try:
                shutil.copy(path_input+'/'+file+'/segment_ph1/visualizations/ph1_contour.gif',
                            path_input + '/GIFs/'+stage_pos_chars[int(file[1:])-1]+'.gif')
            except OSError as e:
                # If it fails, inform the user.
                print('Error: %s - %s.' % (e.filename, e.strerror))

        else:
            try:
                os.makedirs(path_input + '/GIFs')
                shutil.copy(path_input+'/'+file+'/segment_ph1/visualizations/ph1_contour.gif',
                            path_input + '/GIFs/'+stage_pos_chars[int(file[1:])-1]+'.gif')

            except OSError as e:
                # If it fails, inform the user.
                print('Error: %s - %s.' % (e.filename, e.strerror))


# In[10]:


# Config:
images_dir = path_input + '/GIFs/'
result_grid_filename = 'grid.gif'
result_figsize_resolution = 96 # 1 = 100px

images_list = os.listdir(images_dir)
images_count = len(images_list)

# Create plt plot:
fig, axes = plt.subplots(12, 8)

current_file_number = 0
for image_filename in os.listdir(images_dir):

    x_position = int(image_filename[1:].split('.',1)[0])-1
    y_position = ord(image_filename[0])-65

    im = Image.open(images_dir+image_filename).convert('RGB')
    axes[x_position, y_position].imshow(im)
    print((current_file_number + 1), '/', images_count, ': ', image_filename)

    current_file_number += 1

#plt.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)
plt.savefig(result_grid_filename)


# In[ ]:


print('x_pos:', x_position)
print('y_pos:', y_position)
print(image_filename[0])


# In[ ]:


import pyglet
ag_file = "dinosaur-07.gif"

