# import Utility modules
import os
import ast
import datetime
import logging

# import vendor-specific modules
from quixstreams import Application
from quixstreams.models.serializers.quix import JSONDeserializer
from influxdb_client_3 import InfluxDBClient3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Application.Quix(consumer_group="influx-destination",
                       auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"], value_deserializer=JSONDeserializer())

# for debugging only!!!!
# you can make a list directly here in the code and OUTCOMMENT the sections below
#tags = ['country']
#fields = ['timestamp', 'country', 'demand', 'price', 'deficit_surplus']

# Read the environment variable and convert it to a dictionary
tag_dict = ast.literal_eval(os.environ.get('INFLUXDB_TAG_COLUMNS', "{}"))

tag_list = {tag: "" for tag in tag_dict}  # Create a dictionary from the list
# Read the environment variable and convert it to a list
tags_list = ast.literal_eval(os.environ.get('INFLUXDB_TAG_COLUMNS', "[]"))
tag_dict_template = {tag: "" for tag in tags_list}  # Create a dictionary from the list

# Read the environment variable for measurement name
measurement_name = os.environ.get('INFLUXDB_MEASUREMENT_NAME', os.environ["input"])

# Read the environment variable for the field(s) to get.
# For multiple fields, use a list "['field1','field2']"   
fields_list = ast.literal_eval(os.environ.get("INFLUXDB_FIELD_KEYS", "[]"))    
field_dict_template = {field: "" for field in fields_list}  # Create a dictionary from the list                                    
influx3_client = InfluxDBClient3(token=os.environ["INFLUXDB_TOKEN"],
                         host=os.environ["INFLUXDB_HOST"],
                         org=os.environ["INFLUXDB_ORG"],
                         database=os.environ["INFLUXDB_DATABASE"])

def send_data_to_influx(message):
    logger.info(f"Processing message: {message}")
    points = None  # Initialize points to ensure it exists
    try:
        # Extract the timestamp
        quixtime = message['timestamp']

        # Create a tag dictionary based on the template and populate it with values from the message
        tag_dict = {tag: message[tag] for tag in tag_dict_template.keys()}

        # Extract the fields
        field_dict = {field: message[field] for field in field_dict_template if field not in tag_dict_template and field != 'timestamp'}

        logger.info(f"Using fields: {', '.join(field_dict.keys())}")
        logger.info(f"Using tags: {', '.join(tag_dict.keys())}")

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


sdf = app.dataframe(input_topic)
sdf = sdf.update(send_data_to_influx)

if __name__ == "__main__":
    print("Starting application")
    app.run(sdf)