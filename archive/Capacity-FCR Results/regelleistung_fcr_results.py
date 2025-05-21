import pandas as pd
import requests
from datetime import datetime, timedelta
import os

# Define the current date
current_date = datetime.now().strftime('%Y-%m-%d')

# Create the results_xlsx folder if it doesn't exist
results_folder = 'results_xlsx'
os.makedirs(results_folder, exist_ok=True)

# Define the URL with placeholders for date
base_url = "https://www.regelleistung.net/apps/cpp-publisher/api/v1/download/tenders/resultsoverview?date={}&exportFormat=xlsx&market=CAPACITY&productTypes=FCR"

# Build the full URL with the current date
url = base_url.format(current_date)

# Define the output filename with the current date
output_filename = f"{current_date}_capacity_fcr_results.xlsx"

# Add additional value which is used for telegraf to make a proper measurement name
measurement_name = "capacity_fcr_results"

try:
    # Send a GET request to the URL
    response = requests.get(url)

    if response.status_code == 200:
        # Save the content to a file in the results folder
        with open(os.path.join(results_folder, output_filename), 'wb') as file:
            file.write(response.content)

        print(f'File downloaded and saved as {output_filename} in {results_folder}')

    else:
        print(f'File download failed. Status code: {response.status_code}')

except Exception as e:
    print(f'An error occurred during the download: {str(e)}')

# Create the input XLSX filename based on the current date
input_xlsx_file = os.path.join(results_folder, output_filename)
output_csv_file = f'output_{measurement_name}_{current_date}.csv'

def expand_rows_and_add_time(df):
    """Expands rows based on product hours and adds a timestamp."""
    expanded_rows = []
    for _, row in df.iterrows():
        product_parts = row['PRODUCTNAME'].split('_')
        start_hour = int(product_parts[1])
        end_hour = int(product_parts[2])
        
        for hour in range(start_hour, end_hour):
            new_row = row.copy()
            # Check if DATE_FROM is already a datetime object
            if isinstance(row['DATE_FROM'], datetime):
                date_from = row['DATE_FROM']
            else:
                date_from = datetime.strptime(row['DATE_FROM'], '%Y-%m-%d')
            valid_date = date_from + timedelta(hours=hour)
            new_row['date_valid'] = valid_date.strftime('%Y-%m-%dT%H:%M:%S')
            
            # new_row['start_time'] = valid_date.strftime('%Y-%m-%dT%H:%M:%S')
            # end_time = valid_date + timedelta(hours=1) - timedelta(seconds=1)
            # new_row['end_time'] = end_time.strftime('%Y-%m-%dT%H:%M:%S')
            
            expanded_rows.append(new_row)
    
    return pd.DataFrame(expanded_rows)

try:
    df = pd.read_excel(input_xlsx_file)
    df['measurement_name'] = measurement_name
    expanded_df = expand_rows_and_add_time(df)
    expanded_df.to_csv(output_csv_file, index=False)

    print(f'XLSX to CSV conversion successful. CSV file saved as {output_csv_file}')

except Exception as e:
    print(f'XLSX to CSV conversion error: {str(e)}')

# Import shutil for file operations
import shutil

def move_file_to_folder(file_name, target_folder):
    # Create the folder if it doesn't exist
    """Moves a specified file to a target folder, creating the folder if it doesn't
    exist."""
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    # Construct the target path
    target_path = os.path.join(target_folder, file_name)
    
    # Move the file
    shutil.move(file_name, target_path)

# Move the output.csv file to the telegraf_import folder
move_file_to_folder(output_csv_file, 'telegraf_import')
