import datetime
import logging
from quixstreams import Application

logger = logging.getLogger(__name__)

# Define the fields and tags
fields = ['timestamp', 'demand', 'price', 'deficit_surplus']
tags = ['country']
measurement_name = "fcr_results"

def send_data_to_influx(message):
    logger.info(f"Processing message: {message}")
    points = None  # Initialize points to ensure it exists
    try:
        # Extract the timestamp
        quixtime = message['timestamp']

        # Extract the tags
        tag_dict = {tag: message[tag] for tag in tags}

        # Extract the fields
        field_dict = {field: message[field] for field in fields if field not in tags}

        logger.info(f"Using fields: {', '.join(fields)}")
        logger.info(f"Using tags: {', '.join(tags)}")

        # Using point dictionary structure
        points = {
            "measurement": measurement_name,
            "tags": tag_dict,
            "fields": field_dict,
            "time": quixtime
        }

        influx3_client.write(record=points, write_precision="ms")
        
        print(f"{str(datetime.datetime.utcnow())}: Persisted measurement to influx.")
    except KeyError as e:
        logger.error(f"KeyError: {str(e)} - Check if the key exists in the message")
        print(f"{str(datetime.datetime.utcnow())}: Write failed due to missing key")
        print(message)
        print(points)
        raise
    except Exception as e:
        print(f"{str(datetime.datetime.utcnow())}: Write failed")
        print(message)
        print(points)
        raise

# Assuming `app` and `input_topic` are defined elsewhere in your code
app = Application.Quix()
input_topic = "your_input_topic"  # Update with your actual input topic

sdf = app.dataframe(input_topic)
sdf = sdf.update(send_data_to_influx)

if __name__ == "__main__":
    app.run(sdf)
