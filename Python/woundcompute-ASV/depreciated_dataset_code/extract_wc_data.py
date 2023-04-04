#!/usr/bin/env python
# coding: utf-8

# In[209]:


#imports
import os, shutil, fnmatch, time, tkinter
from tkinter.filedialog import askdirectory
from pathlib import Path


# In[210]:


#prompt user for the file directory. Will open as a popup window named "tk"
tk_root = tkinter.Tk()
path_input = askdirectory(title='Select Folder')  # shows dialog box and return the path
print(path_input)
tk_root.destroy()


# In[211]:


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


# In[212]:


for file in os.listdir(path_input):
    if os.path.isdir(path_input + '/' + file):
        #rename file for correct sort syntax
                folder = file.split('s', 1)[-1]

                for num in range(2-len(folder)):
                    folder = '0'+folder
                newfile = 's'+folder
                os.rename(path_input + '/' + file, path_input + '/' + newfile)


# In[212]:





# In[213]:


import pandas as pd
list_pos= []
tlist = [T*0.5 for T in range(1,timepoints_nd+1)]
wa_df = pd.DataFrame({'Frame': range(1,timepoints_nd+1),
                      'Time':  tlist})
for file in os.listdir(path_input):
    if os.path.isdir(path_input+'/'+file):

        list_pos.append(file)
        wa_df[file] = pd.read_table(path_input+'/'+file+'/segment_ph1/wound_area_vs_frame.txt',header = None)

header1 = wa_df.columns
header2 = ['t','Hours']+ stage_pos_chars
wa_df.columns = [header1, header2]
display(wa_df)

xls_name = path_input.split('Code_processed_eclipse_data/',1)[-1].split('/',1)[0]
#wa_df.to_excel(r'E:/Microscope Images/Code_processed_eclipse_data/Wound_area_code_output.xlsx', sheet_name=xls_name+'_'+ basename)

def append_to_excel(fpath, df, sheet_name):
    with pd.ExcelWriter(fpath, mode="a") as f:
        df.to_excel(f, sheet_name=sheet_name)

append_to_excel('E:/Microscope Images/Code_processed_eclipse_data/Wound_area_code_output.xlsx', wa_df,xls_name)


# In[213]:




