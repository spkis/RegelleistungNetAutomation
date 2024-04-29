import pandas as pd
import requests
from datetime import datetime, timedelta 
import openpyxl
import os
import json
# Import the Quix Streams modules for interacting with Kafka:
from quixstreams import Application
from quixstreams.models.serializers.quix import JSONSerializer, SerializationContext

# (see https://quix.io/docs/quix-streams/v2-0-latest/api-reference/quixstreams.html for more details)

# Import additional modules as needed
import pandas as pd
import random
import time
import os

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application.Quix()

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
            new_row['date_valid'] = valid_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:23]
            
            # new_row['start_time'] = valid_date.strftime('%Y-%m-%dT%H:%M:%S')
            # end_time = valid_date + timedelta(hours=1) - timedelta(seconds=1)
            # new_row['end_time'] = end_time.strftime('%Y-%m-%dT%H:%M:%S')
            
            expanded_rows.append(new_row)
    
    return pd.DataFrame(expanded_rows)

try:
    df = pd.read_excel(input_xlsx_file, engine='openpyxl')
    df['measurement_name'] = measurement_name
    expanded_df = expand_rows_and_add_time(df)
    expanded_df.to_csv(output_csv_file, index=False)

    print(f'XLSX to CSV conversion successful. CSV file saved as {output_csv_file}')

except Exception as e:
    print(f'XLSX to CSV conversion error: {str(e)}')

# Stream setup
topic = app.topic(name=os.environ["output"], value_serializer="json")


def send_to_stream(df, topic):
    with app.get_producer() as producer:
        try:
            json_str = df.to_json(orient="records", date_format="iso")
            for row in json.loads(json_str):
                # Extrahiere die TradeId aus der Zeile, um sie als Key zu verwenden
                message_key = f"PRL_DATA_{str(random.randint(1, 100)).zfill(3)}"
                # Konvertiere das Row-Dictionary zu einem JSON-String, um es als Nachricht zu senden
                message = json.dumps(row)
                producer.produce(topic.name, value=message, key=message_key)
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        print("Closing stream")
        producer.flush()
        print("Done.")

send_to_stream(expanded_df, topic)


# def my_task():
#     # Your code here that you want to execute once a day.
#     # Aufruf der Funktion mit dem Pfad auf dem SFTP-Server
#     # Aufruf der Funktion mit dem Pfad auf dem SFTP-Server und Empfang des DataFrames
#     df = retrieve_and_load_data(SFTP_PATH)

#     # Überprüfe, ob df tatsächlich Daten enthält, bevor du ihn weiterverarbeitest
#     if df is not None:
#         send_to_stream(df, topic)
#     else:
#         print("Kein DataFrame zum Senden an den Stream.")

# # send_to_stream(df)

#     print("This task is running daily at the specified time.")

# # Schedule the task to run once a day at a specific time (e.g., 3:30 PM).
# schedule.every().day.at("10:10").do(my_task)

# while True:
#     schedule.run_pending()
#     time.sleep(1)