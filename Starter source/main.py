import pandas as pd
import requests
from datetime import datetime, timedelta
import io  # For handling in-memory bytes objects like files
import os
import json
from quixstreams import Application

app = Application.Quix()


# Define the current date
current_date = datetime.now().strftime('%Y-%m-%d')

# Define the URL with placeholders for date
base_url = "https://www.regelleistung.net/apps/cpp-publisher/api/v1/download/tenders/resultsoverview?date={}&exportFormat=xlsx&market=CAPACITY&productTypes=FCR"

# Build the full URL with the current date
url = base_url.format(current_date)

topic = app.topic(name=os.environ["output"], value_serializer='json')


# strings for key and headers will be serialized to bytes by default
i = 0
with app.get_producer() as producer:

    try:
        # Send a GET request to the URL and load the content directly into a DataFrame
        response = requests.get(url)
        if response.status_code == 200:
            with io.BytesIO(response.content) as file:
                df = pd.read_excel(file)

                json_str = df.to_json(orient='records', lines=True)
                print(json_str)
            
                print(f'Data loaded successfully for {current_date}')

                for row in json.loads(json_str):
                    print(row)
                    producer.produce(topic.name, json.dumps(row), str(row['PRODUCTNAME']))
                    

            # Iterate over the processed DataFrame and send each row as a time series data point
        else:
            print(f'File download failed. Status code: {response.status_code}')
    except Exception as e:
        print(f'An error occurred: {str(e)}')

    # Closing the stream after sending all data points
    print("Closing stream")
    producer.flush()
    print("Done.")
