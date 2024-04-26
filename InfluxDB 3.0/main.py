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

app = Application.Quix(consumer_group="influx-destination-v1",
                       auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"], value_deserializer=JSONDeserializer())

# Read the environment variable and convert it to a dictionary
tag_dict = ast.literal_eval(os.environ.get('INFLUXDB_TAG_COLUMNS', "{}"))

# Read the environment variable for measurement name
measurement_name = os.environ.get('INFLUXDB_MEASUREMENT_NAME', os.environ["input"])

# Read the environment variable for the field(s) to get.
# For multiple fields, use a list "['field1','field2']"
field_keys = os.environ.get("INFLUXDB_FIELD_KEYS", "['PRODUCTNAME','CROSSBORDER_SETTLEMENTCAPACITY_PRICE_[EUR/MW]','AUSTRIA_DEMAND_[MW]','AUSTRIA_SETTLEMENTCAPACITY_PRICE_[EUR/MW]','AUSTRIA_DEFICIT(-)_SURPLUS(+)_[MW]','BELGIUM_DEMAND_[MW]','BELGIUM_SETTLEMENTCAPACITY_PRICE_[EUR/MW]','BELGIUM_DEFICIT(-)_SURPLUS(+)_[MW]','DENMARK_DEMAND_[MW]','DENMARK_SETTLEMENTCAPACITY_PRICE_[EUR/MW]','DENMARK_DEFICIT(-)_SURPLUS(+)_[MW]','FRANCE_DEMAND_[MW]','FRANCE_SETTLEMENTCAPACITY_PRICE_[EUR/MW]','FRANCE_DEFICIT(-)_SURPLUS(+)_[MW]','GERMANY_DEMAND_[MW]','GERMANY_SETTLEMENTCAPACITY_PRICE_[EUR/MW]','GERMANY_DEFICIT(-)_SURPLUS(+)_[MW]','NETHERLANDS_DEMAND_[MW]','NETHERLANDS_SETTLEMENTCAPACITY_PRICE_[EUR/MW]','NETHERLANDS_DEFICIT(-)_SURPLUS(+)_[MW]','SLOVENIA_DEMAND_[MW]','SLOVENIA_SETTLEMENTCAPACITY_PRICE_[EUR/MW]','SLOVENIA_DEFICIT(-)_SURPLUS(+)_[MW]','SWITZERLAND_DEMAND_[MW]','SWITZERLAND_SETTLEMENTCAPACITY_PRICE_[EUR/MW]','SWITZERLAND_DEFICIT(-)_SURPLUS(+)_[MW]','CZECH_REPUBLIC_DEMAND_[MW]','CZECH_REPUBLIC_SETTLEMENTCAPACITY_PRICE_[EUR/MW]','CZECH_REPUBLIC_DEFICIT(-)_SURPLUS(+)_[MW]']")
#field_keys = ast.literal_eval(os.environ.get("INFLUXDB_FIELD_KEYS", "[]"))                                           
influx3_client = InfluxDBClient3(token=os.environ["INFLUXDB_TOKEN"],
                         host=os.environ["INFLUXDB_HOST"],
                         org=os.environ["INFLUXDB_ORG"],
                         database=os.environ["INFLUXDB_DATABASE"])

def send_data_to_influx(message):
    logger.info(f"Processing message: {message}")
    try:
        quixtime = message['date_valid'] #changed from "time"
        # Get the name(s) and value(s) of the selected field(s)
        # Using a single field in this example for simplicity
        field1_name = field_keys[0]
        field1_value = message[field_keys[0]]

        logger.info(f"Using field keys: {', '.join(field_keys)}")

        # Using point dictionary structure
        # See: https://docs.influxdata.com/influxdb/cloud-dedicated/reference/client-libraries/v3/python/#write-data-using-a-dict
        points = {
            "measurement": measurement_name,
            "tags": tag_dict,
            "fields": {field1_name: field1_value},
            "time": quixtime
        }

        influx3_client.write(record=points, write_precision="ms")
        
        print(f"{str(datetime.datetime.utcnow())}: Persisted measurement to influx.")
    except Exception as e:
        print(f"{str(datetime.datetime.utcnow())}: Write failed")
        print(message)
        print(e)
        raise

sdf = app.dataframe(input_topic)
sdf = sdf.update(send_data_to_influx)

if __name__ == "__main__":
    print("Starting application")
    app.run(sdf)