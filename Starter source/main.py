import pandas as pd
import requests
from datetime import datetime, timedelta
import io  # For handling in-memory bytes objects like files
import quixstreams as qx
import os

# Define the current date
current_date = datetime.now().strftime('%Y-%m-%d')

# Define the URL with placeholders for date
base_url = "https://www.regelleistung.net/apps/cpp-publisher/api/v1/download/tenders/resultsoverview?date={}&exportFormat=xlsx&market=CAPACITY&productTypes=FCR"

# Build the full URL with the current date
url = base_url.format(current_date)

# Add additional value which is used for telegraf to make a proper measurement name
measurement_name = "capacity_fcr_results"

# Initialize Quix streaming client
client = qx.QuixStreamingClient()

# Open the output topic where to write data out
topic_producer = client.get_topic_producer(topic_id_or_name=os.environ["QUIX_OUTPUT_TOPIC"])

# Create a stream for the data
stream = topic_producer.create_stream()
stream.properties.name = "Energy Data Stream"

try:
    # Send a GET request to the URL and load the content directly into a DataFrame
    response = requests.get(url)
    if response.status_code == 200:
        with io.BytesIO(response.content) as file:
            df = pd.read_excel(file)
        print(f'Data loaded successfully for {current_date}')

        # Your data processing function here...
        # Assuming it modifies 'df' to become 'expanded_df'
         # Process the DataFrame as before
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
                    new_row['date_valid'] = valid_date.strftime('%Y-%m-%dT%H:%M:%S')
                    expanded_rows.append(new_row)
            
            return pd.DataFrame(expanded_rows)

        # Apply the processing
        df['measurement_name'] = measurement_name
        expanded_df = expand_rows_and_add_time(df)
        

        # Iterate over the processed DataFrame and send each row as a time series data point
        for index, row in expanded_df.iterrows():
            timestamp = pd.to_datetime(row['date_valid'])  # Assuming 'date_valid' is your timestamp column
            parameter_a_value = row['YourDataColumn']  # Replace 'YourDataColumn' with the actual column name you want to stream
            
            # Add data to the stream
            stream.timeseries.buffer.add_timestamp(timestamp) \
                                   .add_value("ParameterA", parameter_a_value) \
                                   .publish()
    else:
        print(f'File download failed. Status code: {response.status_code}')
except Exception as e:
    print(f'An error occurred: {str(e)}')

# Closing the stream after sending all data points
print("Closing stream")
stream.close()
