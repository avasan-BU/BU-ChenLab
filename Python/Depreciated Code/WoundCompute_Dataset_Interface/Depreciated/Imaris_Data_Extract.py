import pandas as pd
import os
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows


def extract_csv_data(folder_path, output_file):
    # Get all CSV files in the folder
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    # Dictionary to store data from each CSV
    data_dict = {}

    for file in csv_files:
        file_path = os.path.join(folder_path, file)

        # Read the CSV file
        with open(file_path, 'r') as f:
            lines = f.readlines()

            # Get the title from the second line
            title = lines[1].strip()

            # Extract data from the first column, starting from the fifth row
            data = [line.split(',')[0].strip() for line in lines[4:]]

            # Store the data in the dictionary
            data_dict[title] = data

    # Find the maximum length of data across all CSVs
    max_length = max(len(data) for data in data_dict.values())

    # Pad shorter lists with None to ensure equal length
    for key in data_dict:
        data_dict[key] += [None] * (max_length - len(data_dict[key]))

    # Create a DataFrame from the dictionary
    df = pd.DataFrame(data_dict)

    # Save the DataFrame to an Excel file
    df.to_excel(output_file, index=False)

    print(f"Data has been saved to {output_file}")

    return df


# Example usage
folder_path = 'E:\\Imaris Data\\20240618_R5P10_11F_H-FN1-Col1_Center_ASV_ChenLab_CF40_Statistics'
output_file = 'E:\\Imaris Data\\output_data_norm.xlsx'
result_df = extract_csv_data(folder_path, output_file)

# Display the first few rows of the resulting DataFrame
print(result_df.head())
