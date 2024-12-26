from influxdb_client import InfluxDBClient
import os

def get_influxdb_client():
    influxdb_url = f"http://{os.getenv('INFLUXDB_SERVER')}"
    influxdb_token = os.getenv('INFLUXDB_TOKEN')
    influxdb_org = os.getenv('INFLUXDB_ORG')
    influxdb_bucket = os.getenv('INFLUXDB_BUCKET')
    
    client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
    return client, influxdb_bucket, influxdb_org