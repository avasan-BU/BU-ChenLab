import os
import glob
import pandas as pd
import numpy as np

# Dictionary to store the data
data_dict = {}

# Find all text files in subfolders
for filepath in glob.glob('C:/Working Folder/20250208_R7P10_NHDFneo_P5_DrugScreen2/Sorted/tissue_ai/s*/**/pillar_tracker_*.txt', recursive=True):
    # Extract the parent folder name (e.g., 'A03')
    parent_folder = os.path.basename(os.path.dirname(os.path.dirname(filepath))).split('_')[1]

    # Determine whether the file is for x or y coordinates
    coordinate_type = 'x' if 'tracker_x' in filepath else 'y'

    # Read the text file with space as delimiter
    df = pd.read_csv(filepath, delimiter=' ', header=None)

    # Ensure the DataFrame has exactly 4 columns, padding missing columns with NaN
    df = df.reindex(columns=range(4), fill_value= np.nan)

    # Initialize an entry for the parent folder if it doesn't exist
    if parent_folder not in data_dict:
        data_dict[parent_folder] = {'x': None, 'y': None, 'distances': None}

    # Store the DataFrame in the appropriate coordinate type (x or y)
    data_dict[parent_folder][coordinate_type] = df



# Function to calculate distances between columns for a given DataFrame
def calculate_distances(x_df, y_df):
    # Ensure both DataFrames have the same shape
    assert x_df.shape == y_df.shape, "X and Y DataFrames must have the same shape"

    # Calculate distances between columns 0 and 1
    dist_0_1 = np.sqrt((x_df.iloc[:, 0] - x_df.iloc[:, 1]) ** 2 + (y_df.iloc[:, 0] - y_df.iloc[:, 1]) ** 2)

    # Calculate distances between columns 1 and 2
    dist_1_2 = np.sqrt((x_df.iloc[:, 1] - x_df.iloc[:, 2]) ** 2 + (y_df.iloc[:, 1] - y_df.iloc[:, 2]) ** 2)

    # Calculate distances between columns 2 and 0
    dist_2_0 = np.sqrt((x_df.iloc[:, 2] - x_df.iloc[:, 0]) ** 2 + (y_df.iloc[:, 2] - y_df.iloc[:, 0]) ** 2)

    return dist_0_1, dist_1_2, dist_2_0


# Calculate and store distances for all folders
for folder_name, folder_data in data_dict.items():
    x_data = folder_data['x']
    y_data = folder_data['y']

    if x_data is not None and y_data is not None:
        # Calculate distances
        dist_0_1, dist_1_2, dist_2_0 = calculate_distances(x_data, y_data)

        # Sort the distances based on their first values
        sorted_distances = sorted([(dist_0_1, 'dist_0_1'), (dist_1_2, 'dist_1_2'), (dist_2_0, 'dist_2_0')],
                                  key=lambda x: x[0].iloc[0], reverse=True)

        # Assign dist_ij, dist_i, and dist_j
        folder_data['dist_ij'] = sorted_distances[0][0]
        folder_data['dist_i'] = sorted_distances[1][0]
        folder_data['dist_j'] = sorted_distances[2][0]

        # Store the original distances for reference
        folder_data['distances'] = {
            'dist_0_1': dist_0_1,
            'dist_1_2': dist_1_2,
            'dist_2_0': dist_2_0
        }


# Create a DataFrame for each distance type to store in Excel
distances_0_1_df = pd.DataFrame()
distances_1_2_df = pd.DataFrame()
distances_2_0_df = pd.DataFrame()
distances_i_df = pd.DataFrame()
distances_j_df = pd.DataFrame()
distances_ij_df = pd.DataFrame()
for folder_name, folder_data in data_dict.items():
    if folder_data['distances'] is not None:
        # Add each distance series as a column in the respective DataFrame
        distances_0_1_df[folder_name] = folder_data['distances']['dist_0_1']
        distances_1_2_df[folder_name] = folder_data['distances']['dist_1_2']
        distances_2_0_df[folder_name] = folder_data['distances']['dist_2_0']
        distances_i_df[folder_name] = folder_data['dist_i']
        distances_j_df[folder_name] = folder_data['dist_j']
        distances_ij_df[folder_name] = folder_data['dist_ij']

# Save to Excel with two sheets: one for 0-1 distances and one for 1-2 distances
output_file = "distances.xlsx"
with pd.ExcelWriter(output_file) as writer:
    distances_0_1_df.to_excel(writer, sheet_name="Distances 0-1", index=False)
    distances_1_2_df.to_excel(writer, sheet_name="Distances 1-2", index=False)
    distances_2_0_df.to_excel(writer, sheet_name="Distances 2-0", index=False)
    distances_i_df.to_excel(writer, sheet_name="Distances i", index=False)
    distances_j_df.to_excel(writer, sheet_name="Distances j", index=False)
    distances_ij_df.to_excel(writer, sheet_name="Distances ij", index=False)

print(f"Distances have been saved to {output_file}")