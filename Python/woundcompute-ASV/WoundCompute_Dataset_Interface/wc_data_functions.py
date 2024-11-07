import os
import pandas as pd
import openpyxl
import matplotlib.pyplot as plt
import re


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


    folder_list = [f.name for f in folder_path_list]
    return dfs, metrics, folder_list

def append_to_excel(fpath, df, sheet_name):
    if not os.path.exists(fpath):
        workbook = openpyxl.Workbook()
        workbook.save(fpath)
    with pd.ExcelWriter(fpath, mode="a", if_sheet_exists='replace') as f:
        df.to_excel(f, sheet_name=sheet_name)

def visualize_data(path_output_in, basename_in, image_type_in, all_data_in, metrics_in, positions_in, assigned_df_in):
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
        pattern = re.compile(r'([A-H]\d{2})')
        positions_filtered = [pattern.search(pos).group(0) for pos in positions_in if pattern.search(pos) is not None]

        for condition in assigned_df_in['Condition_Name'].unique():
            wells = assigned_df_in[assigned_df_in['Condition_Name'] == condition]['Well']
            wells = [pos for pos in positions_in if any(well in pos for well in wells)]
            grouped_data[condition] = df[wells]

        # Plot data for each condition
        plt.figure(figsize=(10, 6))
        mean = {}
        std = {}
        for condition_name, data_list in grouped_data.items():
            mean[condition_name] = data_list.mean(axis=1)
            std[condition_name] = data_list.std(axis=1)

            plt.plot(time_hours, mean[condition_name], label=condition_name)
            plt.fill_between(time_hours, mean[condition_name] - std[condition_name], mean[condition_name] + std[condition_name], alpha=0.2)

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

