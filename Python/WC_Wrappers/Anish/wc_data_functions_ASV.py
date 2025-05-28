import os
from tokenize import group

import pandas as pd
import openpyxl
import matplotlib.pyplot as plt
import re

from numpy.lib.index_tricks import index_exp


# DATA EXTRACTION AND VISUALIZATION FUNCTIONS #
def extract_data(path_input_fn: str, basename_fn: str, image_type: str, interval_in: int, df_assignments_in) -> (dict,list) :
    folder_path_list = sorted(os.scandir(os.path.join(path_input_fn, basename_fn)), key=lambda x: x.name)
    folder_path_list = [n1 for n1 in folder_path_list if os.path.isdir(n1)]

    frames = len(os.listdir(os.path.join(folder_path_list[0].path, image_type + "_images")))
    metrics = [f for f in os.listdir(os.path.join(folder_path_list[0].path, "segment_" + image_type)) if f.endswith(".txt")]
    tlist = [T * interval_in for T in range(0, frames)]

    dfs = {}

    if not os.path.exists(os.path.join(path_input_fn, 'code_output_' + basename_fn + '.xlsx')):
        workbook = openpyxl.Workbook()
        workbook.save(os.path.join(path_input_fn, 'code_output_' + basename_fn + '.xlsx'))
    metrics = [f for f in metrics if f != 'tissue_parameters_vs_frame.txt']
    for metric in metrics:

            print(f"Extracting data for {metric.split('_vs_')[0]}...")
            dfs[metric.split('_vs_')[0]] = pd.DataFrame({'Frame': range(1, frames + 1), 'Time': tlist})

            for file in folder_path_list:
                dfs[metric.split('_vs_')[0]][file.name] = pd.read_table(os.path.join(file.path, 'segment_' + image_type, metric), header=None, dtype=float)

            append_to_excel(os.path.join(path_input_fn, 'code_output_' + basename_fn + '.xlsx'), dfs[metric.split('_vs_')[0]], metric.split('_vs_')[0])

    # Extract pillar tracking data
    #df_pt = pd.DataFrame({'Frame': range(1, frames + 1), 'Time': tlist})
    #for file in folder_path_list:
        #df_pt[file.name] = pd.read_csv(file_path, sep='\t', header=None, names=['col1', 'col2', 'col3'])
        #



    folder_list = [f.name for f in folder_path_list]


    return dfs, metrics, folder_list


def append_to_excel(fpath, df, sheet_name):
    if not os.path.exists(fpath):
        workbook = openpyxl.Workbook()
        workbook.save(fpath)
    with pd.ExcelWriter(fpath, mode="a", if_sheet_exists='replace') as f:
        df.to_excel(f, sheet_name=sheet_name)

def visualize_data(path_output_in, basename_in, all_data_in, metrics_in, positions_in, assigned_df_in):
    """
       Visualizes data from all_data_in by plotting metrics over time per condition.

       Parameters:
       - path_output_in: str, path to save output images
       - basename_in: str, base name for output files
       - image_type_in: str, image file type (e.g., 'png', 'jpg')
       - all_data_in: dict, contains dataframes for each metric
       - metrics_in: list, metrics to be plotted
       - positions_in: list, positions to be considered
       - assigned_df_in: DataFrame, contains condition assignments for positions
       """
    # Create a folder to store the visualizations
    if not os.path.exists(os.path.join(path_output_in, basename_in + '_visualizations')):
        os.makedirs(os.path.join(path_output_in, basename_in + '_visualizations'))

    # Create a folder to store the visualizations
    if not os.path.exists(os.path.join(path_output_in, basename_in + '_visualizations', 'segmentation')):
        os.makedirs(os.path.join(path_output_in, basename_in + '_visualizations', 'segmentation'))
    for metric in metrics_in:
        metric = metric.split('_vs_')[0]
        df = all_data_in[metric]
        time_hours = df['Time']  # Convert time to hours


        # Group data by condition
        grouped_data = {}
        mean = {}
        std = {}
        # Plot data for each condition
        plt.figure(figsize=(10, 6))
        for condition in assigned_df_in['Condition_Name'].unique():
            wells = assigned_df_in[assigned_df_in['Condition_Name'] == condition]['Well']
            wells = [pos for pos in positions_in if any(well in pos for well in wells)]
            grouped_data[condition] = df[wells]
            df_grouped = pd.DataFrame(grouped_data[condition])
            df_grouped['Time'] = time_hours
            df_grouped = df_grouped[['Time'] + list(df_grouped.columns[:-1])]
            append_to_excel(os.path.join(path_output_in, basename_in + '_visualizations', metric, basename_in + '_' + metric + '.xlsx'), df_grouped, condition)

            if condition != 'Faulty':
                mean[condition] = grouped_data[condition].mean(axis=1)
                std[condition] = grouped_data[condition].std(axis=1)
                plt.plot(time_hours, mean[condition], label=condition)
                plt.fill_between(time_hours, mean[condition] - std[condition], mean[condition] + std[condition], alpha=0.2)

        plt.title(f'{metric} vs Time')
        plt.xlabel('Time (Hours)')
        plt.ylabel(metric)
        plt.legend()
        plt.grid(True)

        # Create a folder to store the visualizations
        if not os.path.exists(os.path.join(path_output_in, basename_in + '_visualizations', metric)):
            os.makedirs(os.path.join(path_output_in, basename_in + '_visualizations', metric))

        # Save the plot
        output_filename =os.path.join(path_output_in, basename_in + '_visualizations', metric, basename_in + '_' + metric + '.png')
        plt.savefig(output_filename)
        plt.close()
        print(f"Plots saved in ", output_filename)



def messy_requests(path_output_in,basename_in, df_grouped_in, all_data_in):
    #Normalized wound area
    wa = df_grouped_in['wound_area']
    wa_norm=wa.copy()
    time_hours = all_data_in['wound_area']['Time']
    time_max = {}
    for condition in wa_norm.keys():
        #time_hours = wa_norm[condition]['Time']
        #wa_norm[condition].drop(columns=['Time'])
        wa_norm[condition] = wa_norm[condition].div(wa_norm[condition].iloc[0])

        # Time to max opening
        index_max = wa_norm[condition].idxmax()
        time_max[condition] = index_max/2

        # append_to_excel(os.path.join(path_output_in, basename_in + '_visualizations', 'wound_area', basename_in + '_time2max.xlsx'), time_max[condition], condition)

        


    print(f"Time to max opening: {time_max}")

def group_data(all_data_in, metrics_in, positions_in, df_assignments_in)-> dict:
    """
    Groups data by conditions based on the assigned_df_in DataFrame.

    Parameters:
    - all_data_in: dict, contains dataframes for each metric
    - metrics_in: list, metrics to be grouped
    - positions_in: list, positions to be considered
    - df_assignments_in: DataFrame, contains condition assignments for positions
    """
    df_grouped = {}
    for metric in metrics_in:
        metric = metric.split('_vs_')[0]
        df = all_data_in[metric]
        time_hours = df['Time']

        # Group data by condition
        grouped_data = {}
        mean = {}
        std = {}
        for condition in df_assignments_in['Condition_Name'].unique():
            wells = df_assignments_in[df_assignments_in['Condition_Name'] == condition]['Well']
            wells = [pos for pos in positions_in if any(well in pos for well in wells)]
            grouped_data[condition] = df[wells]

            df_grouped[metric] = pd.DataFrame(grouped_data[condition])
            df_grouped[metric]['Time'] = time_hours
            df_grouped[metric] = df_grouped[metric][['Time'] + list(df_grouped[metric].columns[:-1])]


        df_grouped[metric] = grouped_data

    return df_grouped